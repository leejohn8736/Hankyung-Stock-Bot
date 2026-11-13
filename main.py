name: Unified Stock Alert Bot

on:
  schedule:
    # 한국 시간(KST) 기준 평일 오전 6시 40분 (UTC 21:40) & 오후 4시 40분 (UTC 07:40)
    - cron: "40 21 * * 0-4"
    - cron: "40 7 * * 1-5"
  workflow_dispatch:
    inputs:
      market:
        description: "실행할 시장 선택 (KR / US / ALL)"
        default: "ALL"
        type: string

permissions:
  contents: write

concurrency:
  group: unified-stock-bot
  cancel-in-progress: false

jobs:
  run-all-bots:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          # 만약 로컬 패키지 구조(setup.py 등)가 있다면 함께 설치
          if [ -f setup.py ] || [ -f pyproject.toml ]; then pip install --editable .; fi

      - name: Pick market (Optional parameter)
        id: m
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            M="${{ github.event.inputs.market }}"
          else
            M="ALL"
          fi
          [ "$M" = "ALL" ] && M="KR US"
          echo "markets=$M" >> "$GITHUB_OUTPUT"

      - name: 1. Run Naver Stock Ranking & Briefing Bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          echo "🚀 네이버 실시간 검색어 및 브리핑 봇 실행..."
          if [ -f main.py ]; then python main.py; fi

      - name: 2. Run BNF / Signal Stock Analysis Bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          echo "📊 주식 신호 및 테마 분석 봇 실행..."
          if [ -f bnf_signal.py ]; then python bnf_signal.py ${{ steps.m.outputs.markets }}; fi

      - name: Commit and Push results (if any changed)
        run: |
          git config user.name "bot-runner"
          git config user.email "bot-runner@users.noreply.github.com"
          git add data/ docs/ data/ranking.json state/ || true
          git diff --cached --quiet || git commit -m "auto: update stock rankings and signal data [skip ci]"
          git pull --rebase && git push || echo "No changes to push or push skipped."
