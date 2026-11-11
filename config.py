import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MONITOR_START_HOUR = 4
MONITOR_END_HOUR = 24

MIN_RESERVE_RATIO = 300.0

RSS_FEEDS = {
    "한경_전체": "https://www.hankyung.com/feed/all-news",
    "한경_증권": "https://www.hankyung.com/feed/finance",
    "한경_경제": "https://www.hankyung.com/feed/economy",
    "한경_부동산": "https://www.hankyung.com/feed/realestate",
    "한경_IT": "https://www.hankyung.com/feed/it",
    "매경_경제": "https://www.mk.co.kr/rss/30100041/",
    "매경_기업경영": "https://www.mk.co.kr/rss/50100032/",
    "매경_증권": "https://www.mk.co.kr/rss/50200011/",
    "매경TV_증권": "https://mbnmoney.mbn.co.kr/rss/news/stock",
    "서경_금융": "https://www.sedaily.com/rss/finance",
    "뉴스핌_산업": "http://rss.newspim.com/news/category/106",
    "뉴스핌_증권금융": "http://rss.newspim.com/news/category/105",
    "뉴스핌_글로벌": "http://rss.newspim.com/news/category/107",
}

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
