from datetime import datetime, timedelta
import pandas as pd
from pykrx import stock
import requests
from config import MIN_RESERVE_RATIO


def load_krx_stocks():
  """스팩, 우선주, 리츠 등을 제외한 코스피/코스닥 일반종목 로드 (날짜 예외 처리 강화)"""
  # 안전하게 오늘 날짜부터 역순으로 영업일 탐색
  today_dt = datetime.now()
  stock_map = {}
  exclude_words = (
      "스팩",
      "우",
      "우B",
      "우C",
      "리츠",
      "인버스",
      "레버리지",
      "ETF",
      "ETN",
  )

  latest_day = None
  for i in range(7):  # 최대 7일 전까지 탐색
    target_date = (today_dt - timedelta(days=i)).strftime("%Y%m%d")
    try:
      tickers = stock.get_market_ticker_list(target_date, market="KOSPI")
      if tickers and len(tickers) > 0:
        latest_day = target_date
        break
    except Exception:
      continue

  # 만약 영업일을 못 찾았다면 오늘 날짜 문자열 사용
  if not latest_day:
    latest_day = today_dt.strftime("%Y%m%d")

  print(f"[KRX] 기준일자: {latest_day} 종목 마스터 로드 시작...")

  for market in ["KOSPI", "KOSDAQ"]:
    try:
      tickers = stock.get_market_ticker_list(latest_day, market=market)
      for t in tickers:
        name = stock.get_market_ticker_name(t)
        if t.endswith("0") and not name.endswith(exclude_words) and len(name) >= 2:
          stock_map[name] = {"ticker": t, "market": market}
    except Exception as e:
      print(f"[경고] {market} 종목 로드 중 예외 발생: {e}")

  print(f"[KRX 로드 완료] 총 {len(stock_map)}개 일반종목 마스터 로드")
  return stock_map


def check_financials(ticker):
  """네이버 금융 재무제표 크롤링: 영업이익 상승 및 유보율 검증"""
  url = f"https://finance.naver.com/item/main.naver?code={ticker}"
  headers = {"User-Agent": "Mozilla/5.0"}
  try:
    res = requests.get(url, headers=headers, timeout=5)
    tables = pd.read_html(res.text)

    fin_df = None
    for df in tables:
      if "주요재무정보" in str(df.columns) or "영업이익" in str(df.iloc[:, 0].values):
        fin_df = df
        break

    if fin_df is None:
      return False, None

    fin_df.columns = [
        col[1] if isinstance(col, tuple) else col for col in fin_df.columns
    ]
    fin_df = fin_df.set_index(fin_df.columns[0])

    annual_cols = [c for c in fin_df.columns if "." in str(c)][:4]
    if len(annual_cols) < 2:
      return False, None

    op_row = fin_df.loc["영업이익", annual_cols].dropna()
    op_vals = pd.to_numeric(op_row, errors="coerce").dropna().values
    if len(op_vals) < 2:
      return False, None

    is_op_growing = (op_vals[-1] > op_vals[-2]) and (op_vals[-1] > 0)

    res_row = fin_df.loc["유보율", annual_cols].dropna()
    res_vals = pd.to_numeric(res_row, errors="coerce").dropna().values
    latest_reserve = res_vals[-1] if len(res_vals) > 0 else 0

    is_reserve_good = latest_reserve >= MIN_RESERVE_RATIO

    if is_op_growing and is_reserve_good:
      info = {
          "op_prev": op_vals[-2],
          "op_curr": op_vals[-1],
          "reserve": latest_reserve,
      }
      return True, info
  except Exception:
    pass

  return False, None
