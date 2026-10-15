goto :comment
@echo off
cd /d "C:\Users\User\Documents\GitHub\Dashboard"

echo [1/5] Updating Notion export...
python notion.py

echo [2/5] Updating Blogger export...
python blogger.py

echo [3/5] Updating Google Docs export...
python docs.py

echo [4/5] Updating Google Sheets export...
python sheets.py

echo [5/5] Starting local server and opening Content Hub...
start http://localhost:8000/contentHub.html
python -m http.server 8000
:comment