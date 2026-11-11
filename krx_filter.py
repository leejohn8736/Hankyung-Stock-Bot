from datetime import datetime, timedelta
import pandas as pd
from pykrx import stock
import requests
from config import MIN_RESERVE_RATIO


def load_krx_stocks():
  """일반주와 우선주/스팩(잡주)을 모두 정상 로드합니다."""
  today_dt = datetime.now()
  stock_map = {}

  latest_day = None
  for i in range(7):
    target_date = (today_dt - timedelta(days=i)).strftime("%Y%m%d")
    try:
      tickers = stock.get_market_ticker_list(target_date, market="KOSPI")
      if tickers and len(tickers) > 0:
        latest_day = target_date
        break
    except Exception:
      continue

  if not latest_day:
    latest_day = today_dt.strftime("%Y%m%d")

  print(f"[KRX] 기준일자: {latest_day} 종목 마스터 로드 시작...")

  for market in ["KOSPI", "KOSDAQ"]:
    try:
      tickers = stock.get_market_ticker_list(latest_day, market=market)
      for t in tickers:
        name = stock.get_market_ticker_name(t)
        if len(name) < 2:
          continue

        # ETF, ETN, 인버스, 리츠 제외
        if any(x in name for x in ["인버스", "레버리지", "ETF", "ETN", "리츠"]):
          continue

        # 📌 우선주(끝자리 0이 아니거나 '우'로 끝남) 및 스팩을 잡주로 정상 분류
        is_special = (
            not t.endswith("0")
            or name.endswith(("우", "우B", "우C"))
            or "스팩" in name
        )

        stock_map[name] = {
            "ticker": t,
            "market": market,
            "is_special": is_special,
        }
    except Exception as e:
      print(f"[경고] {market} 종목 로드 중 예외 발생: {e}")

  print(f"[KRX 로드 완료] 총 {len(stock_map)}개 종목 마스터 로드")
  return stock_map


def check_financials(ticker, is_special=False):
  """재무제표 검증 (잡주/우선주는 재무 데이터가 없어도 뉴스 호재만으로 통과 허용)"""
  if is_special:
    return True, {"op_prev": 0, "op_curr": 0, "reserve": 0}

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

    is_op_good = op_vals[-1] > 0

    res_row = fin_df.loc["유보율", annual_cols].dropna()
    res_vals = pd.to_numeric(res_row, errors="coerce").dropna().values
    latest_reserve = res_vals[-1] if len(res_vals) > 0 else 0

    is_reserve_good = latest_reserve >= MIN_RESERVE_RATIO

    if is_op_good and is_reserve_good:
      info = {
          "op_prev": op_vals[-2],
          "op_curr": op_vals[-1],
          "reserve": latest_reserve,
      }
      return True, info
  except Exception:
    pass

  return False, None
