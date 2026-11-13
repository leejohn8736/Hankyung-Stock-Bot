def fetch_stock_rankings():
    """네이버 금융 실시간 주식 검색어 상위 20개 수집 (안정성 강화 버전)"""
    url = "https://finance.naver.com/sise/lastsearch2.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://finance.naver.com/"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html_bytes = response.read()
            html_content = html_bytes.decode('euc-kr', 'replace')
            
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 특정 클래스(.type_5)뿐만 아니라 페이지 내의 모든 주소 테이블 행(tr)을 유연하게 탐색
        ranking_list = []
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            # 네이버 금융 검색 상위 테이블 행은 보통 10개 이상의 컬럼을 가짐
            if len(cols) >= 10:
                name_tag = cols[1].find('a')
                if not name_tag or 'code=' not in name_tag.get('href', ''):
                    continue
                
                try:
                    rank = cols[0].text.strip()
                    name = name_tag.text.strip()
                    code = name_tag['href'].split('code=')[-1]
                    search_ratio = cols[2].text.strip()
                    current_price = cols[3].text.strip()
                    change_rate = cols[5].text.strip()
                    
                    ranking_list.append({
                        "rank": int(rank) if rank.isdigit() else len(ranking_list) + 1,
                        "name": name,
                        "code": code,
                        "search_ratio": search_ratio,
                        "price": current_price,
                        "change_rate": change_rate
                    })
                    
                    if len(ranking_list) >= 20:
                        break
                except Exception:
                    continue
                    
        return ranking_list
    except Exception as e:
        print(f"❌ 주식 크롤링 오류: {e}")
        return []
