#!/bin/zsh

# Navigate to the project directory if running outside it
cd "$(dirname "$0")"

echo "[1/5] Updating Notion export..."
python3 notion.py

echo "[2/5] Updating Blogger export..."
python3 blogger.py

echo "[3/5] Updating Google Docs export..."
python3 docs.py

echo "[4/5] Updating Google Sheets export..."
python3 sheets.py

echo "[5/5] Starting local server and opening Content Hub..."
open http://localhost:8000/contentHub.html
python3 -m http.server 8000