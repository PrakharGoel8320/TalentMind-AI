# TalentMind AI — Helper Scripts

This directory contains convenience scripts to seed data, launch services, and run automated tests.

---

## 🚀 Available Scripts

### 1. `seed_demo.bat` (or PowerShell / Bash)
Initializes the database schema and seeds the standard demo job (*Senior Backend Engineer - AI Platform*) and 4 differentiated candidate profiles.
```cmd
scripts\seed_demo.bat
```
*Equivalent command:* `cd backend && poetry run python -m app.seed_demo`

---

### 2. `start_backend.bat`
Starts the FastAPI backend on `http://127.0.0.1:8000`.
```cmd
scripts\start_backend.bat
```
*Equivalent command:* `cd backend && poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

---

### 3. `start_frontend.bat`
Starts the Next.js frontend development server on `http://localhost:3000`.
```cmd
scripts\start_frontend.bat
```
*Equivalent command:* `cd frontend && npm run dev`

---

### 4. `run_tests.bat`
Executes both backend (89 tests) and frontend (3 tests) test suites.
```cmd
scripts\run_tests.bat
```
*Equivalent command:* `cd backend && poetry run pytest tests -v && cd ../frontend && npm test`
