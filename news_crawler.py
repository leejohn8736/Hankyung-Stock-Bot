from bs4 import BeautifulSoup
import requests
from config import POSITIVE_KEYWORDS


def collect_recent_news(stock_map):
  """네이버 뉴스 실시간 검색을 통해 키워드와 매칭되는 최신 기사를 수집합니다."""
  candidates = {"KOSPI": [], "KOSDAQ": []}
  sorted_names = sorted(stock_map.keys(), key=len, reverse=True)
  seen_links = set()

  # 주요 검색 키워드 몇 가지를 조합하여 실시간 뉴스 검색 수행
  search_queries = [
      "반도체 AI 수혜",
      "방산 원전 조선",
      "제약 바이오",
      "증권 주식 특징주",
      "삼성전자 SK하이닉스 현대차",
  ]

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  for query in search_queries:
    url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"  # sort=1 (최신순)
    try:
      res = requests.get(url, headers=headers, timeout=5)
      if res.status_code != 200:
        continue

      soup = BeautifulSoup(res.text, "html.parser")
      news_items = soup.select(".news_area")

      for item in news_items:
        title_tag = item.select_one(".news_title")
        if not title_tag:
          continue

        title = title_tag.get_text().strip()
        link = title_tag.attrs.get("href", "").strip()

        if not link or link in seen_links:
          continue

        # 호재/감시 키워드 포함 여부 확인
        score = sum(2 for kw in POSITIVE_KEYWORDS if kw in title)
        if score == 0:
          continue

        # 종목명 매칭 확인
        for name in sorted_names:
          if name in title:
            seen_links.add(link)
            info = stock_map[name]
            candidates[info["market"]].append({
                "name": name,
                "ticker": info["ticker"],
                "market": info["market"],
                "is_special": info["is_special"],
                "section": "실시간뉴스검색",
                "title": title,
                "link": link,
                "score": score,
            })
            break
    except Exception as e:
      print(f"[크롤링 경고] 검색어 '{query}' 처리 중 오류: {e}")

  print(
      f"[뉴스 수집 완료] 후보군 - 코스피: {len(candidates['KOSPI'])}건, "
      f"코스닥: {len(candidates['KOSDAQ'])}건"
  )
  return candidates
