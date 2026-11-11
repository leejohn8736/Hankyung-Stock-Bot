import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MONITOR_START_HOUR = 4
MONITOR_END_HOUR = 24

MIN_RESERVE_RATIO = 300.0

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

# 📌 요청하신 모든 감시 키워드 및 기존 호재 키워드 통합 반영
POSITIVE_KEYWORDS = [
    # 요청하신 핵심 테마 및 종목 키워드
    "삼성전자",
    "AI",
    "반도체",
    "증권",
    "부동산",
    "한국항공우주",
    "방산",
    "원전",
    "조선",
    "금리",
    "주식",
    "현대차",
    "SK하이닉스",
    "배터리",
    "데이터 센타",
    "데이터 센터",
    "금",
    "전쟁",
    "제약주",
    "바이오",
    "통신",
    "보안",
    "보안주",
    "게임",
    # 기존 증권가 호재/상승 키워드
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
    "목표가",
    "상향",
    "매수",
    "랠리",
    "신고가",
    "독점",
    "특허",
    "승인",
    "양산",
    "전환",
    "개선",
    "확대",
    "기대",
    "상승",
    "호조",
    "협약",
    "MOU",
    "투자",
    "출시",
    "선정",
    "1위",
    "유망",
    "저평가",
    "배당",
    "자사주",
]
