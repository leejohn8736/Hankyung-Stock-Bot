"""
국내 주식 실시간 검색 순위 텔레그램 봇 (다중 소스 폴백 버전)

수집 우선순위
  1) 네이버 금융 '검색상위 종목' (진짜 실시간 검색어 순위, TOP 30 중 20개 사용)
  2) 다음 금융 '실시간 검색 순위' (JSON API, 최대 10개)
  3) 네이버 모바일 증권 시가총액 상위 (대체 데이터)
  4) FinanceDataReader 시가총액 상위 (최후의 대체 데이터)

앞 소스가 실패하면 자동으로 다음 소스로 넘어가고,
전부 실패하면 '왜 실패했는지'를 텔레그램으로 알려줍니다.
"""
import os
import re
import sys
import json
import time
import html
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

KST = timezone(timedelta(hours=9))
TOP_N = 20

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
FORCE_RUN = os.environ.get("FORCE_RUN") == "1"  # 수동 실행 시 운영시간 검사 무시

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.5",
    "Accept": "text/html,application/json,*/*;q=0.8",
}


# ───────────────────────── 공통 유틸 ─────────────────────────
def http_get(url, retries=3, timeout=15, **kwargs):
    """재시도 포함 GET. 실패 시 마지막 예외를 그대로 raise."""
    headers = dict(HEADERS)
    headers.update(kwargs.pop("headers", {}))
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            r.raise_for_status()
            return r
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def to_float(v):
    try:
        return float(str(v).replace(",", "").replace("%", "").replace("+", "").strip())
    except Exception:
        return None


def fmt_rate(v):
    """등락률을 '+1.23%' 형태로 통일 (부호가 이미 있는 값 기준)."""
    f = to_float(v)
    if f is None:
        return "-"
    return f"{f:+.2f}%"


def fmt_price(v):
    f = to_float(v)
    if f is None:
        return str(v)
    return f"{int(f):,}"


def rate_icon(rate_str):
    f = to_float(rate_str)
    if f is None or f == 0:
        return "➖"
    return "🔺" if f > 0 else "🔻"


def check_operating_time():
    now = datetime.now(KST)
    minutes = now.hour * 60 + now.minute
    return 4 * 60 <= minutes <= 23 * 60


def send_telegram_msg(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_BOT_TOKEN(또는 TELEGRAM_TOKEN) / TELEGRAM_CHAT_ID 값이 비어 있습니다.")
        print("   → GitHub Secrets 이름과 run.yml의 env 이름이 일치하는지 확인하세요.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            # 토큰 오류/chat_id 오류 등 원인을 로그에 그대로 출력
            print(f"❌ 텔레그램 응답 {r.status_code}: {r.text[:300]}")
            return False
        return True
    except Exception as e:
        print(f"❌ 텔레그램 발송 오류: {e}")
        return False


# ───────────────────────── 수집 소스 ─────────────────────────
def source_naver_search():
    """네이버 금융 검색상위 종목 (실시간 검색 순위)"""
    url = "https://finance.naver.com/sise/lastsearch2.naver"
    r = http_get(url, headers={"Referer": "https://finance.naver.com/sise/"})
    page = r.content.decode("cp949", errors="replace")
    soup = BeautifulSoup(page, "lxml")

    table = soup.select_one("table.type_5") or soup.select_one("table.type_2")
    if table is None:
        raise ValueError("검색상위 테이블을 찾지 못함(페이지 구조 변경 또는 차단 페이지)")

    items = []
    for tr in table.select("tr"):
        a = tr.select_one("a[href*='code=']")
        tds = tr.find_all("td")
        if not a or len(tds) < 6:
            continue
        m = re.search(r"code=(\d{6})", a.get("href", ""))
        if not m:
            continue
        texts = [td.get_text(strip=True) for td in tds]
        # 열 순서: 순위 | 종목명 | 검색비율 | 현재가 | 전일비 | 등락률 | 거래량 ...
        items.append({
            "rank": len(items) + 1,
            "name": a.get_text(strip=True),
            "code": m.group(1),
            "price": texts[3],
            "rate": fmt_rate(texts[5]),
            "extra": f"검색 {texts[2]}" if texts[2] else "",
        })
        if len(items) >= TOP_N:
            break
    return items


def source_daum_search():
    """다음 금융 실시간 검색 순위 (JSON)"""
    url = "https://finance.daum.net/api/search/ranks?limit=10"
    r = http_get(url, headers={
        "Referer": "https://finance.daum.net/",
        "Accept": "application/json, text/plain, */*",
    })
    data = r.json().get("data", [])
    items = []
    for d in data:
        code = str(d.get("symbolCode", "")).lstrip("A")
        rate = (d.get("changeRate") or 0) * 100
        if d.get("change") == "FALL":
            rate = -abs(rate)
        elif d.get("change") == "RISE":
            rate = abs(rate)
        else:
            rate = 0
        items.append({
            "rank": d.get("rank", len(items) + 1),
            "name": d.get("name", "?"),
            "code": code,
            "price": fmt_price(d.get("tradePrice", "-")),
            "rate": fmt_rate(rate),
            "extra": "",
        })
    return items[:TOP_N]


def source_naver_marketcap():
    """네이버 모바일 증권 시가총액 상위 (검색순위 아님, 대체용)"""
    url = "https://m.stock.naver.com/api/stocks/marketValue/KOSPI?page=1&pageSize=20"
    r = http_get(url, headers={"Referer": "https://m.stock.naver.com/"})
    stocks = r.json().get("stocks", [])
    items = []
    for s in stocks:
        items.append({
            "rank": len(items) + 1,
            "name": s.get("stockName", "?"),
            "code": s.get("itemCode", ""),
            "price": fmt_price(s.get("closePrice", "-")),
            "rate": fmt_rate(s.get("fluctuationsRatio", "0")),
            "extra": "",
        })
    return items[:TOP_N]


def source_fdr_marketcap():
    """FinanceDataReader 시가총액 상위 (검색순위 아님, 최후의 대체용)"""
    import pandas as pd
    import FinanceDataReader as fdr

    df = pd.concat([fdr.StockListing("KOSPI"), fdr.StockListing("KOSDAQ")], ignore_index=True)
    if "Marcap" in df.columns:
        df = df.sort_values("Marcap", ascending=False)
    items = []
    for _, row in df.head(TOP_N).iterrows():
        rate = row.get("ChagesRatio", row.get("ChangesRatio", 0))
        items.append({
            "rank": len(items) + 1,
            "name": row.get("Name", "?"),
            "code": str(row.get("Code", "")),
            "price": fmt_price(row.get("Close", "-")),
            "rate": fmt_rate(rate),
            "extra": "",
        })
    return items


# (키, 표시 이름, 함수, 실제 '검색 순위'인지 여부)
SOURCES = [
    ("naver_search", "네이버 금융 검색상위 종목", source_naver_search, True),
    ("daum_search", "다음 금융 실시간 검색 순위", source_daum_search, True),
    ("naver_marketcap", "네이버 시가총액 상위(대체)", source_naver_marketcap, False),
    ("fdr_marketcap", "FinanceDataReader 시가총액(대체)", source_fdr_marketcap, False),
]


def collect():
    errors = {}
    for key, label, fn, is_search in SOURCES:
        try:
            print(f"📊 [{key}] 수집 시도...")
            items = fn()
            if len(items) >= 5:
                print(f"✅ [{key}] {len(items)}개 수집 성공")
                return items, label, is_search, errors
            errors[key] = f"결과 부족({len(items)}개)"
        except Exception as e:
            errors[key] = f"{type(e).__name__}: {str(e)[:120]}"
        print(f"⚠️ [{key}] 실패: {errors[key]}")
    return [], None, False, errors


# ───────────────────────── 메시지/저장 ─────────────────────────
def build_message(items, label, is_search, errors, now_str):
    title = "실시간 검색 순위 TOP" if is_search else "시가총액 상위 TOP"
    lines = [
        f"📈 <b>국내 증시 {title} {len(items)}</b>",
        f"⏱ <i>{now_str} (KST)</i>",
        f"🔎 출처: {html.escape(label)}",
        "",
    ]
    for it in items:
        name = html.escape(str(it["name"]))
        link = f"https://finance.naver.com/item/main.naver?code={it['code']}"
        line = (
            f"<b>{it['rank']}</b>. <a href='{link}'>{name}</a> "
            f"{it['price']}원 {rate_icon(it['rate'])}{it['rate']}"
        )
        if it.get("extra"):
            line += f" · {html.escape(it['extra'])}"
        lines.append(line)

    if not is_search:
        lines += ["", "⚠️ 검색 순위 소스가 모두 실패해 대체 데이터(시가총액)를 보냈습니다."]
    if errors:
        short = ", ".join(f"{k}" for k in errors)
        lines += ["", f"ℹ️ 실패한 소스: {html.escape(short)}"]
    return "\n".join(lines)


def save_json(items, label, errors, now_str):
    os.makedirs("data", exist_ok=True)
    with open("data/ranking.json", "w", encoding="utf-8") as f:
        json.dump(
            {"updated_at": now_str, "source": label, "errors": errors, "items": items},
            f, ensure_ascii=False, indent=2,
        )


def main():
    print("🚀 국내 주식 순위 봇 시작")
    if not FORCE_RUN and not check_operating_time():
        print("💤 운영 시간(04:00~23:00 KST) 외라 종료합니다.")
        return

    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    items, label, is_search, errors = collect()

    if not items:
        detail = "\n".join(f"• {html.escape(k)}: {html.escape(v)}" for k, v in errors.items())
        send_telegram_msg(f"❌ <b>주식 순위 수집 실패</b> ({now_str})\n{detail}")
        print("❌ 모든 소스 실패")
        sys.exit(1)

    save_json(items, label, errors, now_str)
    ok = send_telegram_msg(build_message(items, label, is_search, errors, now_str))
    print("✅ 텔레그램 발송 성공" if ok else "❌ 텔레그램 발송 실패")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
