import feedparser
from config import POSITIVE_KEYWORDS, RSS_FEEDS


def collect_recent_news(stock_map):
  """RSS 피드를 스캔하여 최근 호재 종목 후보군 추출 (Actions 1회 실행용)"""
  candidates = {"KOSPI": [], "KOSDAQ": []}
  sorted_names = sorted(stock_map.keys(), key=len, reverse=True)

  for section, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
      link = entry.get("link", "").strip()
      title = entry.get("title", "").strip()

      if not link:
        continue

      score = sum(2 for kw in POSITIVE_KEYWORDS if kw in title)
      if score == 0:
        continue

      for name in sorted_names:
        if name in title:
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

  return candidates
