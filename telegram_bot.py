from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import requests


def send_telegram(message):
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("[오류] 텔레그램 토큰 또는 챗 ID가 설정되지 않았습니다.")
    return

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": message,
      "parse_mode": "HTML",
      "disable_web_page_preview": True,
  }
  try:
    res = requests.post(url, json=payload, timeout=10)
    if not res.ok:
      print(f"[텔레그램 전송 실패] 응답 코드: {res.status_code}")
  except Exception as e:
    print(f"[텔레그램 오류] {e}")
