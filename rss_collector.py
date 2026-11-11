import calendar
import time
import feedparser
from config import POSITIVE_KEYWORDS, RSS_FEEDS


def collect_recent_news(stock_map):
  """여러 언론사 RSS 피드를 스캔하여 정확한 24시간 이내 최신 뉴스를 수집합니다."""
  candidates = {"KOSPI": [], "KOSDAQ": []}
  sorted_names = sorted(stock_map.keys(), key=len, reverse=True)

  seen_links = set()
  now_timestamp = time.time()
  time_threshold = 24 * 60 * 60  # 최근 24시간

  for section, url in RSS_FEEDS.items():
    try:
      feed = feedparser.parse(url)
      for entry in feed.entries:
        link = entry.get("link", "").strip()
        if not link or link in seen_links:
          continue

        # 📌 time.mktime 대신 calendar.timegm을 사용하여 UTC 시차 오차 제거
        pub_parsed = entry.get("published_parsed")
        if pub_parsed:
          pub_timestamp = calendar.timegm(pub_parsed)
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
                "is_special": info["is_special"],
                "section": section,
                "title": title,
                "link": link,
                "score": score,
            })
            break
    except Exception as e:
      print(f"[RSS 수집 경고] {section} 채널 파싱 중 오류 발생: {e}")

  print(
      f"[RSS 수집 완료] 후보군 - 코스피: {len(candidates['KOSPI'])}건, "
      f"코스닥: {len(candidates['KOSDAQ'])}건"
  )
  return candidates
