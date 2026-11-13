  # 📈 실시간 국내 주식 검색어 순위 알림 봇
##네이버 금융의 실시간 인기 검색어 상위 20개 종목을 자동으로 수집하고, 지정된 시간에 맞춰 텔레그램(Telegram)으로 브리핑을 발송하는 자동화 프로젝트입니다.
✨ 주요 기능
- 실시간 검색어 TOP 20 수집: 국내 증시(KOSPI · KOSDAQ) 기준 투자자들이 가장 많이 검색한 상위 20개 종목의 순위, 현재가, 등락률, 검색 비율을 정밀하게 추출합니다.
- 스마트 운영 시간 방어 로직: 한국 시간(KST) 기준 매일 새벽 04:00 ~ 밤 23:00 사이에만 동작하도록 설계되어 불필요한 심야 알림을 방지합니다.
- 정기 알림 스케줄링 (GitHub Actions): 별도의 개인 서버 없이 GitHub 클라우드 환경에서 매일 오전 06:00부터 밤 21:00까지 2시간 간격으로 자동 실행됩니다.
- 데이터 자동 백업 및 웹 연동: 수집된 데이터는 data/ranking.json 파일로 저장되며, GitHub Pages(index.html)를 통해 웹 대시보드로도 즉시 확인할 수 있습니다.
⏰ 자동 실행 스케줄
구분설정 시간 (KST 기준)비고시스템 운영 허용 시간04:00 ~ 23:00외 시간대 실행 시 방어 로직 작동 (자동 종료)정기 텔레그램 발송 주기06:00 ~ 21:00 (2시간 간격)06시, 08시, 10시, 12시, 14시, 16시, 18시, 20시, 21시수동 테스트 실행상시 가능GitHub Actions 탭에서 Run workflow 클릭


 # ⚙️ 설치 및 설정 방법
## 1. 필수 라이브러리 목록 (requirements.txt)
Plaintext
requests==2.32.3
beautifulsoup4==4.12.3
lxml==5.3.0
2. 깃허브 시크릿(Secrets) 설정
레포지토리의 Settings → Secrets and variables → Actions에서 아래 두 가지 비밀 값을 등록해야 텔레그램 발송이 정상 작동합니다.

TELEGRAM_TOKEN: 텔레그램 BotFather를 통해 발급받은 봇 토큰

TELEGRAM_CHAT_ID: 메시지를 받을 채팅방(또는 채널) ID

3. GitHub Actions 권한 설정
레포지토리 Settings → Actions → General → Workflow permissions로 이동합니다.

Read and write permissions를 체크하고 저장(Save)합니다. (자동 커밋/푸시 권한 부여)

<img width="616" height="357" alt="image" src="https://github.com/user-attachments/assets/4b19a5f0-6eef-447a-9692-1b0d0957e77a" />


