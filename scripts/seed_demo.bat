@echo off
echo Seeding TalentMind AI demo data...
cd /d "%~dp0\..\backend"
poetry run python -m app.seed_demo
if %ERRORLEVEL% EQU 0 (
    echo Demo data seeded successfully!
) else (
    echo Error seeding demo data.
)
pause
