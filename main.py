from datetime import datetime
import pytz
from config import MONITOR_END_HOUR, MONITOR_START_HOUR
from krx_filter import check_financials, load_krx_stocks
from news_crawler import collect_recent_news
from telegram_bot import send_telegram

KST = pytz.timezone("Asia/Seoul")


def main():
  # 1. 시간 검증 (KST 기준 04:00 ~ 24:00)
  now_kst = datetime.now(KST)
  current_hour = now_kst.hour

  if not (MONITOR_START_HOUR <= current_hour < MONITOR_END_HOUR):
    print(
        f"[{now_kst.strftime('%H:%M:%S')}] 운영 시간이 아닙니다."
        " (모니터링 시간: 04:00~24:00 KST)"
    )
    return

  time_str = now_kst.strftime("%Y-%m-%d %H:%M:%S")
  print(f"[{time_str}] 실시간 키워드 뉴스 봇 실행 시작 (KST)")

  # 2. KRX 종목 마스터 로드 및 실시간 뉴스 수집
  stock_map = load_krx_stocks()
  candidates = collect_recent_news(stock_map)

  # 3. 시장별, 유형별(일반주 / 잡주) 최고 점수 종목 각각 1개씩 선별 (총 4개)
  selected = {
      "KOSPI_normal": None,
      "KOSPI_special": None,
      "KOSDAQ_normal": None,
      "KOSDAQ_special": None,
  }

  for market in ["KOSPI", "KOSDAQ"]:
    sorted_cands = sorted(
        candidates[market], key=lambda x: x["score"], reverse=True
    )
    checked_tickers = set()

    for cand in sorted_cands:
      ticker = cand["ticker"]
      if ticker in checked_tickers:
        continue
      checked_tickers.add(ticker)

      key_type = "special" if cand["is_special"] else "normal"
      slot_key = f"{market}_{key_type}"
      if selected[slot_key] is not None:
        continue

      passed, fin_info = check_financials(ticker, is_special=cand["is_special"])
      if passed:
        cand["fin"] = fin_info
        selected[slot_key] = cand

      if all(v is not None for v in selected.values()):
        break

  # 4. 결과 발송 (종목이 하나도 없어도 텔레그램 발송)
  now_str = now_kst.strftime("%Y-%m-%d %H:%M")
  has_any = any(v is not None for v in selected.values())

  if has_any:
    msg_lines = [
        f"<b>🚨 [실시간 키워드 뉴스 수혜종목 (총 4선)]</b>\n⏱ {now_str} (KST)\n"
    ]

    categories = [
        ("코스피 일반주", "KOSPI_normal"),
        ("코스피 잡주(우선주/스팩)", "KOSPI_special"),
        ("코스닥 일반주", "KOSDAQ_normal"),
        ("코스닥 잡주(우선주/스팩)", "KOSDAQ_special"),
    ]

    for label, key in categories:
      item = selected.get(key)
      if item:
        fin = item["fin"]
        if item["is_special"]:
          fin_text = "• 재무: 우선주/스팩 (실시간 키워드 매칭)\n"
        else:
          fin_text = (
              f"• 영업이익: {fin['op_prev']:,.0f}억 ➔ <b>{fin['op_curr']:,.0f}억</b>\n"
              f"• 유보율: <b>{fin['reserve']:,.1f}%</b>\n"
          )
        msg_lines.append(
            f"<b>■ {label}: {item['name']} ({item['ticker']})</b>\n"
            f"{fin_text}"
            f"• 뉴스: <a href=\"{item['link']}\">{item['title']}</a>\n"
        )
      else:
        msg_lines.append(f"<b>■ {label}: 조건 충족 종목 없음</b>\n")

    final_msg = "\n".join(msg_lines)
  else:
    final_msg = (
        f"<b>🚨 [실시간 키워드 뉴스 수혜종목]</b>\n⏱ {now_str} (KST)\n\n"
        "• 현재 조건 충족 종목 없음 (모니터링 정상 작동 중)"
    )

  print(final_msg)
  send_telegram(final_msg)


if __name__ == "__main__":
  main()
