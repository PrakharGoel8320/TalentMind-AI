@echo off
echo Running TalentMind AI Backend Tests (Pytest)...
cd /d "%~dp0\..\backend"
poetry run pytest tests -v
if %ERRORLEVEL% NEQ 0 (
    echo Backend tests failed!
    exit /b %ERRORLEVEL%
)

echo Running TalentMind AI Frontend Tests (Jest)...
cd /d "%~dp0\..\frontend"
call npm test
if %ERRORLEVEL% NEQ 0 (
    echo Frontend tests failed!
    exit /b %ERRORLEVEL%
)

echo All backend and frontend tests passed successfully!
pause
