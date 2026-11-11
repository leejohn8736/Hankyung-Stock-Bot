from datetime import datetime, timezone
import time
import feedparser
from config import POSITIVE_KEYWORDS, RSS_FEEDS


def collect_recent_news(stock_map):
  """여러 언론사 RSS 피드를 스캔하여 1시간 이내 최신 기사만 골라내고 중복 링크를 제거합니다."""
  candidates = {"KOSPI": [], "KOSDAQ": []}
  sorted_names = sorted(stock_map.keys(), key=len, reverse=True)

  seen_links = set()  # 중복 뉴스 링크 방지용 세트
  now_timestamp = time.time()
  time_threshold = 60 * 60  # 60분 (1시간) 이내 기사만 허용

  for section, url in RSS_FEEDS.items():
    try:
      feed = feedparser.parse(url)
      for entry in feed.entries:
        link = entry.get("link", "").strip()
        if not link or link in seen_links:
          continue

        # 발행 시간 검증 (published_parsed가 있는 경우 최신성 필터링)
        pub_parsed = entry.get("published_parsed")
        if pub_parsed:
          pub_timestamp = time.mktime(pub_parsed)
          if (now_timestamp - pub_timestamp) > time_threshold:
            continue

        title = entry.get("title", "").strip()
        score = sum(2 for kw in POSITIVE_KEYWORDS if kw in title)
        if score == 0:
          continue

        for name in sorted_names:
          if name in title:
            seen_links.add(link)
            info = stock_map[name]
            candidates[info["market"]].append({
                "name": name,
                "ticker": info["ticker"],
                "market": info["market"],
                "section": section,
                "title": title,
                "link": link,
                "score": score,
            })
            break
    except Exception as e:
      print(f"[RSS 수집 경고] {section} 채널 파싱 중 오류 발생: {e}")

  return candidates
