import feedparser
from config import POSITIVE_KEYWORDS, RSS_FEEDS


def collect_recent_news(stock_map):
  """여러 언론사(한경, 매경, 서경, 뉴스핌 등) RSS 피드를 스캔하여 호재 후보군 추출"""
  candidates = {"KOSPI": [], "KOSDAQ": []}
  sorted_names = sorted(stock_map.keys(), key=len, reverse=True)

  # 여러 언론사 RSS 채널을 순회하며 뉴스 수집
  for section, url in RSS_FEEDS.items():
    try:
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
    except Exception as e:
      print(f"[RSS 수집 경고] {section} 채널 파싱 중 오류 발생: {e}")

  return candidates
