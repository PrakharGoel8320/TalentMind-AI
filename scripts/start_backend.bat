@echo off
echo Starting TalentMind AI Backend on http://127.0.0.1:8000 ...
cd /d "%~dp0\..\backend"
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
