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

# 📈 확장된 다중 언론사 RSS 피드 주소 딕셔너리
RSS_FEEDS = {
    # 한국경제
    "한경_전체": "https://www.hankyung.com/feed/all-news",
    "한경_증권": "https://www.hankyung.com/feed/finance",
    "한경_경제": "https://www.hankyung.com/feed/economy",
    "한경_부동산": "https://www.hankyung.com/feed/realestate",
    "한경_IT": "https://www.hankyung.com/feed/it",
    # 매일경제
    "매경_경제": "https://www.mk.co.kr/rss/30100041/",
    "매경_기업경영": "https://www.mk.co.kr/rss/50100032/",
    "매경_증권": "https://www.mk.co.kr/rss/50200011/",
    # 매일경제TV
    "매경TV_증권": "https://mbnmoney.mbn.co.kr/rss/news/stock",
    # 서울경제
    "서경_금융": "https://www.sedaily.com/rss/finance",
    # 뉴스핌
    "뉴스핌_산업": "http://rss.newspim.com/news/category/106",
    "뉴스핌_증권금융": "http://rss.newspim.com/news/category/105",
    "뉴스핌_글로벌": "http://rss.newspim.com/news/category/107",
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
