# 📈 Hankyung Real-time Stock News RSS Bot (GitHub Actions)

한국경제 RSS 피드를 실시간으로 모니터링하여, 뉴스 속 호재 키워드가 포함된 종목 중 **영업이익이 증가하고 유보율이 500% 이상인 우량 일반 종목**을 코스피 1개, 코스닥 1개씩 선별하여 매 12분마다 텔레그램으로 자동 발송해 주는 서버리스(Serverless) 파이썬 봇입니다.

## 🕒 운영 시간 및 주기
- **모니터링 시간:** 매일 한국 시간(KST) **새벽 04:00 ~ 저녁 21:00**
- **실행 주기:** 정확히 **매 12분 간격** (GitHub Actions Cron 활용)

---

## 📂 프로젝트 구조

```text
hankyung-stock-bot/
├── .github/
│   └── workflows/
│       └── run.yml          # GitHub Actions 자동화 스케줄러 (12분 주기)
├── .gitignore               # 보안 파일(.env) 및 캐시 제외 설정
├── config.py                # 환경 변수 및 공통 설정 관리
├── rss_collector.py         # 한국경제 5개 RSS 피드 수집 및 뉴스 매칭
├── krx_filter.py            # KRX 일반종목 로드 및 네이버 금융 재무 필터
├── telegram_bot.py          # 비노출형 토큰 기반 텔레그램 전송 모듈
├── main.py                  # 메인 실행 스크립트 (KST 시간 검증 및 프로세스 총괄)
├── requirements.txt         # 필수 라이브러리 목록
└── README.md                # 프로젝트 설명서
