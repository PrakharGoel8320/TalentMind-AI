# TalentMind AI 🚀

An **AI-powered recruiter platform** that evaluates, ranks, and acts on candidates using a deterministic intelligence pipeline, LangGraph agent orchestration, and human-in-the-loop approval for all external actions.

![Overview](docs/images/slide_1_img_0.png)

## Key Features

* **Deterministic Candidate Intelligence**: FAISS retrieval → feature extraction → Cross-Encoder reranking → behavioral scoring → fusion/ranking
* **LangGraph Agent**: Plans, uses pipeline tools, proposes actions (never executes directly)
* **Human-in-the-Loop**: All external actions require recruiter approval before execution
* **Mock/Real Provider Boundaries**: Email (mock/SMTP) and LLM (mock/Ollama/OpenAI) clearly separated

### System Architecture

![System Architecture](docs/images/slide_2_img_1.png)

## Getting Started

### Prerequisites

- Python 3.12+ with [Poetry](https://python-poetry.org/)
- Node.js 18+
- Copy `.env.example` to `backend/.env`

### Backend (FastAPI)

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — login with any non-empty email/password (demo auth).

### Environment Setup

Minimum variables (see `.env.example` for full list):

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
JWT_SECRET=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EMAIL_MODE=mock
LLM_PROVIDER=mock
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Database Seeding (Demo Data)

```bash
cd backend
poetry run python -m app.seed_demo
```

This seeds a realistic demo job (*Senior Backend Engineer - AI Platform*) and 4 deterministic candidate profiles for immediate presentation.

### Running Tests

```bash
# Backend (89 tests including determinism verification)
cd backend && poetry run pytest tests -v

# Frontend Unit Tests
cd frontend && npm test

# Frontend Production Build Check
cd frontend && npm run build

# Playwright E2E User Journey Tests
cd frontend && npx playwright test
```

## Demo Workflow

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for the full hackathon demo path:

1. Login → Dashboard → Candidates → Jobs
2. Rank candidates (deterministic pipeline)
3. Agent Panel → ask recruiter questions → propose email action
4. Approvals → Approve → Execute → mock email recorded as EXECUTED

## Mock vs Real Providers

| Provider | Default | Env Variable |
|----------|---------|--------------|
| Email | Mock (no real send) | `EMAIL_MODE=mock` or `smtp` |
| LLM Agent | Mock | `LLM_PROVIDER=mock`, `ollama`, or `openai` |
| Auth | Demo (any credentials) | Production would use real user DB |

## Technologies

* **Frontend**: Next.js 14, React, TailwindCSS, TanStack Query, Framer Motion
* **Backend**: FastAPI, Python 3.12, SQLAlchemy, Poetry
* **ML**: SentenceTransformers, FAISS, Cross-Encoder, LangGraph
* **Safety**: Human approval queue, `assert_action_approved` guard

## Documentation

- [Executive Project Summary](docs/PROJECT_SUMMARY.md) — one-page architectural & value overview
- [Judge Demo Script (3-Minute Walkthrough)](docs/JUDGE_DEMO_SCRIPT.md) — live hackathon presentation guide
- [Judge Q&A & Technical Defense](docs/JUDGE_QA.md) — 16 technical defense answers
- [Evidence Index](docs/EVIDENCE_INDEX.md) — source code and test mapping for all claims
- [Demo Guide](docs/DEMO_GUIDE.md) — step-by-step setup and demo path
- [Troubleshooting & Diagnostics](docs/TROUBLESHOOTING.md) — failure recovery guide
- [Submission Checklist](docs/SUBMISSION_CHECKLIST.md) — pre-submission verification checklist
- [Part 12 Completion Report](docs/PART_12_COMPLETION_REPORT.md) — final engineering audit report

---
*Built for the India Runs Data & AI Challenge.*
