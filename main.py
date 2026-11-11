from datetime import datetime
import pytz
from config import MONITOR_END_HOUR, MONITOR_START_HOUR
from krx_filter import check_financials, load_krx_stocks
from rss_collector import collect_recent_news
from telegram_bot import send_telegram

KST = pytz.timezone("Asia/Seoul")


def main():
  # 1. 시간 검증 (KST 기준 새벽 04:00 ~ 자정 24:00 인지 확인)
  now_kst = datetime.now(KST)
  current_hour = now_kst.hour

  if not (MONITOR_START_HOUR <= current_hour < MONITOR_END_HOUR):
    print(
        f"[{now_kst.strftime('%H:%M:%S')}] 운영 시간이 아닙니다."
        " (모니터링 시간: 04:00~24:00 KST)"
    )
    return

  time_str = now_kst.strftime("%Y-%m-%d %H:%M:%S")
  print(f"[{time_str}] 봇 실행 시작 (KST)")

  # 2. KRX 종목 로드 및 1시간 이내 최신 뉴스 수집
  stock_map = load_krx_stocks()
  candidates = collect_recent_news(stock_map)

  # 3. 시장별 최고 점수 종목 선별 및 재무 검증
  selected = {}
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

      passed, fin_info = check_financials(ticker)
      if passed:
        cand["fin"] = fin_info
        selected[market] = cand
        break

  # 4. 결과 발송 (조건 충족 종목이 없어도 텔레그램 전송)
  now_str = now_kst.strftime("%Y-%m-%d %H:%M")
  if selected.get("KOSPI") or selected.get("KOSDAQ"):
    msg_lines = [f"<b>🚨 [통합 경제지 실시간 수혜종목]</b>\n⏱ {now_str} (KST)\n"]

    for market_label, key in [("코스피", "KOSPI"), ("코스닥", "KOSDAQ")]:
      item = selected.get(key)
      if item:
        fin = item["fin"]
        msg_lines.append(
            f"<b>■ {market_label}: {item['name']} ({item['ticker']})</b>\n"
            f"• 영업이익: {fin['op_prev']:,.0f}억 ➔ <b>{fin['op_curr']:,.0f}억"
            " (증가)</b>\n"
            f"• 유보율: <b>{fin['reserve']:,.1f}%</b>\n"
            f"• 뉴스({item['section']}):"
            f' <a href="{item["link"]}">{item["title"]}</a>\n'
        )
      else:
        msg_lines.append(
            f"<b>■ {market_label}: 조건 충족 종목 없음</b>\n"
        )

    final_msg = "\n".join(msg_lines)
    print(final_msg)
    send_telegram(final_msg)
  else:
    no_result_msg = (
        f"<b>🚨 [통합 경제지 실시간 수혜종목]</b>\n⏱ {now_str}"
        " (KST)\n\n• 1시간 이내 조건 충족 종목 없음."
    )
    print(f"[{now_str}] 1시간 이내 조건 충족 종목 없음.")
    send_telegram(no_result_msg)


if __name__ == "__main__":
  main()
