import os
from dotenv import load_dotenv

# 로컬 테스트 시 .env 로드, GitHub Actions에서는 시스템 환경 변수 사용
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 모니터링 시간 설정 (KST 기준: 새벽 04시 ~ 저녁 21시)
MONITOR_START_HOUR = 4
MONITOR_END_HOUR = 21

# 재무 건전성 필터 기준 (유보율 500% 이상)
MIN_RESERVE_RATIO = 500.0

# 한국경제 RSS 피드 주소 딕셔너리
RSS_FEEDS = {
    "전체": "https://www.hankyung.com/feed/all-news",
    "증권": "https://www.hankyung.com/feed/finance",
    "경제": "https://www.hankyung.com/feed/economy",
    "부동산": "https://www.hankyung.com/feed/realestate",
    "IT": "https://www.hankyung.com/feed/it",
}

# 뉴스 호재 가중치 키워드
POSITIVE_KEYWORDS = [
    "수혜",
    "급등",
    "상한가",
    "최대",
    "호실적",
    "흑자",
    "수주",
    "계약",
    "공급",
    "신기록",
    "강세",
    "반등",
    "성장",
    "돌파",
    "개발",
    "인수",
    "특징주",
]
