import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

# 1. 텔레그램 설정값 가져오기
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
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
    current_hour = now_kst.hour
    current_minute = now_kst.minute
    
    # 총 분(minute)으로 환산하여 비교 (04:00 = 240분, 23:00 = 1380분)
    current_total_minutes = current_hour * 60 + current_minute
    start_limit = 4 * 60       # 새벽 4시 00분
    end_limit = 23 * 60        # 밤 23시 00분
    
    if start_limit <= current_total_minutes <= end_limit:
        return True
    return False

def fetch_stock_rankings():
    """네이버 금융 실시간 주식 검색어 상위 20개 수집"""
    url = "https://finance.naver.com/sise/lastsearch2.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html_bytes = response.read()
            html_content = html_bytes.decode('euc-kr', 'replace')
            
        soup = BeautifulSoup(html_content, 'lxml')
        table = soup.find('table', {'class': 'type_5'})
        if not table:
            print("⚠️ 데이터 테이블을 찾을 수 없습니다.")
            return []
            
        rows = table.find_all('tr')
        ranking_list = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 10:
                rank = cols[0].text.strip()
                name_tag = cols[1].find('a')
                if not name_tag:
                    continue
                    
                name = name_tag.text.strip()
                code = name_tag['href'].split('code=')[-1]
                search_ratio = cols[2].text.strip()
                current_price = cols[3].text.strip()
                change_rate = cols[5].text.strip()
                
                ranking_list.append({
                    "rank": int(rank),
                    "name": name,
                    "code": code,
                    "search_ratio": search_ratio,
                    "price": current_price,
                    "change_rate": change_rate
                })
                
                # 상위 20개만 추출
                if len(ranking_list) >= 20:
                    break
        return ranking_list
    except Exception as e:
        print(f"❌ 주식 크롤링 오류: {e}")
        return []

def main():
    print("🚀 실시간 국내 주식 검색어 봇 실행 중...")
    
    # 1. 방어로직: 운영 시간(새벽 4시 ~ 밤 11시) 체크
    if not check_operating_time():
        print("💤 현재 운영 시간이 아닙니다. (새벽 04시 ~ 저녁 23시 외 시간)")
        return
        
    # 2. 주식 데이터 수집 (상위 20개)
    rankings = fetch_stock_rankings()
    if not rankings:
        print("⚠️ 수집된 주식 데이터가 없습니다.")
        return
        
    kst = timezone(timedelta(hours=9))
    update_time_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. 텔레그램 메시지 포맷팅
    message_lines = [
        f"📈 <b>실시간 국내 주식 검색어 순위 TOP 20</b>",
        f"⏱ <i>기준 시각: {update_time_str} (KST)</i>\n"
    ]
    
    for item in rankings:
        rate = item['change_rate']
        emoji = "🔴" if "+" in rate else ("🔵" if "-" in rate else "⚪")
        
        line = f"<b>{item['rank']}위</b>. <a href='https://finance.naver.com/item/main.naver?code={item['code']}'>{item['name']}</a> | <b>{item['price']}원</b> ({emoji} {rate})"
        message_lines.append(line)
        
    final_message = "\n".join(message_lines)
    
    # 4. 텔레그램 발송
    if send_telegram_msg(final_message):
        print("✅ 주식 검색어 순위 20개 텔레그램 발송 성공!")
    else:
        print("❌ 텔레그램 발송 실패")

if __name__ == "__main__":
    main()
