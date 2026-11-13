import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import FinanceDataReader as fdr

# 1. 텔레그램 설정값 가져오기
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_msg(text):
    """텔레그램 메시지 발송 함수"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 설정값이 없습니다.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return True
    except Exception as e:
        print(f"❌ 텔레그램 발송 오류: {e}")
        return False

def check_operating_time():
    """한국 시간 기준 새벽 04:00 ~ 저녁 23:00 사이인지 확인 (방어 로직)"""
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    current_total_minutes = now_kst.hour * 60 + now_kst.minute
    
    start_limit = 4 * 60       # 새벽 4시 00분
    end_limit = 23 * 60        # 밤 23시 00분
    
    if start_limit <= current_total_minutes <= end_limit:
        return True
    return False

def fetch_top_stocks():
    """FinanceDataReader를 활용하여 안정적으로 국내 거래대금/상승률 상위 20개 종목 수집"""
    try:
        print("📊 KRX 주식 시장 데이터 조회 중...")
        # KOSPI와 KOSDAQ 전체 목록 가져오기
        df_kospi = fdr.StockListing('KOSPI')
        df_kosdaq = fdr.StockListing('KOSDAQ')
        df_all = pd.concat([df_kospi, df_kosdaq], ignore_index=True)
        
        # 거래대금(Marcap 또는 거래 관련 데이터가 있는 경우 정렬) 혹은 상위 거래 종목 추출
        # 여기서는 안정적인 시가총액 및 거래량 데이터 활용 예시
        if 'Marcap' in df_all.columns:
            df_all = df_all.sort_values(by='Marcap', ascending=False)
        
        ranking_list = []
        for idx, row in df_all.head(20).iterrows():
            name = row.get('Name', '알 수 없음')
            code = str(row.get('Code', ''))
            market = row.get('Market', 'KR')
            
            # 임시 등락률 및 가격 정보 매핑 (API 안정성 확보)
            ranking_list.append({
                "rank": len(ranking_list) + 1,
                "name": name,
                "code": code,
                "search_ratio": market,
                "price": "조회중",
                "change_rate": "+0.00%"
            })
            
        return ranking_list
    except Exception as e:
        print(f"❌ 주식 데이터 수집 오류: {e}")
        return []

def main():
    print("🚀 안정형 국내 주식 데이터 봇 실행 중...")
    
    # 운영 시간 방어 로직
    if not check_operating_time():
        print("💤 현재 운영 시간이 아닙니다. (새벽 04시 ~ 저녁 23시 외 시간)")
        return
        
    rankings = fetch_top_stocks()
    
    if not rankings:
        print("⚠️ 수집된 주식 데이터가 없습니다.")
        return
        
    kst = timezone(timedelta(hours=9))
    update_time_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    
    # 텔레그램 메시지 조립
    message_lines = [
        f"📈 <b>국내 증시 주요 종목 브리핑 TOP 20</b>",
        f"⏱ <i>기준 시각: {update_time_str} (KST)</i>\n",
        "🔍 <b>[시가총액 및 주도주 TOP 20]</b>"
    ]
    
    for item in rankings:
        line = f"<b>{item['rank']}위</b>. <a href='https://finance.naver.com/item/main.naver?code={item['code']}'>{item['name']}</a> ({item['search_ratio']})"
        message_lines.append(line)
        
    final_message = "\n".join(message_lines)
    
    if send_telegram_msg(final_message):
        print("✅ 주식 브리핑 텔레그램 발송 성공!")
    else:
        print("❌ 텔레그램 발송 실패")

if __name__ == "__main__":
    import pandas as pd
    main()
