# TalentMind AI 🚀

An **AI-powered recruiter platform** that evaluates, ranks, and acts on candidates using a deterministic intelligence pipeline, LangGraph agent orchestration, and human-in-the-loop approval for all external actions.

## 🎯 Problem
Recruiters spend countless hours manually parsing resumes and comparing candidates against job descriptions, often relying on biased heuristics. Black-box AI tools exist, but they lack explainability and often hallucinate or make decisions without proper human oversight.

## 💡 Solution
TalentMind AI solves this by employing a completely **deterministic ML pipeline** alongside an agentic layer. We leverage FAISS for fast retrieval, SentenceTransformers & CrossEncoders for deterministic semantic ranking, and LangGraph for reasoning. Crucially, **every agent action is gated by a human approval queue**, providing full explainability and safety.

## ✨ Key Features
* **Deterministic Candidate Intelligence**: FAISS retrieval → deterministic feature extraction → Cross-Encoder reranking → behavioral scoring → fusion ranking.
* **LangGraph Agent**: Plans, uses pipeline tools, and proposes actions (never executes directly).
* **Human-in-the-Loop**: All external actions require recruiter approval before execution.
* **Mock/Real Provider Boundaries**: Email (mock/SMTP) and LLM (mock/Ollama/OpenAI) clearly separated.

## 🏗 System Architecture
![System Architecture](docs/images/slide_2_img_1.png)

## 💻 Tech Stack
* **Frontend**: Next.js 14, React, TailwindCSS, TanStack Query, Framer Motion
* **Backend**: FastAPI, Python 3.12, SQLAlchemy, asyncpg, Poetry
* **Data Layer**: PostgreSQL (primary), Redis (optional), Neo4j (optional)
* **ML/AI**: PyTorch (CPU-optimized), SentenceTransformers, FAISS, Cross-Encoder, LangGraph

## 📁 Project Structure
```text
TalentMind AI/
├── backend/          # FastAPI server, ML pipelines, and Agent logic
├── frontend/         # Next.js 14 dashboard
├── infra/            # Docker, local setup files
└── docs/             # Documentation and screenshots
```

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL (or use SQLite for dev)

### Environment Variables
Copy `.env.example` to `backend/.env` and `frontend/.env.local`

**Minimum `backend/.env`:**
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
# For production: postgresql+asyncpg://user:pass@host/db
JWT_SECRET=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EMAIL_MODE=mock
LLM_PROVIDER=mock
```

**Minimum `frontend/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Running Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*Note: We recommend setting up a virtual environment first.*

**Database Seeding (Demo Data):**
```bash
cd backend
python -m app.seed_demo
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000 — login with any non-empty email/password (demo auth).

## 🌍 Deployment
This repository is optimized for **Render** (Backend) and **Vercel** (Frontend).
- **Backend (Render):**
  - Environment: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - RAM: 512 MiB minimum (Models are lazy-loaded to prevent OOM)
- **Frontend (Vercel):**
  - Framework: Next.js
  - Build Command: `npm run build`

### 🔗 Live Demo
* [Frontend Live URL](https://talentmind-ai-frontend.vercel.app/) *(example link)*
* [Backend Health Endpoint](https://talentmind-ai-backend.onrender.com/api/v1/health) *(example link)*

## 🔗 Important API Endpoints
* `GET /api/v1/health` - Fast, non-blocking health check (used by Render)
* `GET /api/v1/readiness` - Full ML readiness probe
* `POST /api/v1/jobs/{job_id}/rank` - Run deterministic ranking pipeline
* `POST /api/v1/agent/chat` - Interact with the LangGraph orchestrator
* `POST /api/v1/approvals/{id}/approve` - Human-in-the-loop approval execution

## 📸 Screenshots
*(No screenshots available in this environment. Replace with real ones if they exist in docs/images)*
![Overview](docs/images/slide_1_img_0.png)

## 📚 Documentation
- [Executive Project Summary](docs/PROJECT_SUMMARY.md)
- [Judge Demo Script (3-Minute Walkthrough)](docs/JUDGE_DEMO_SCRIPT.md)
- [Judge Q&A & Technical Defense](docs/JUDGE_QA.md)
- [Evidence Index](docs/EVIDENCE_INDEX.md)
- [Demo Guide](docs/DEMO_GUIDE.md)

---
*Built for the India Runs Data & AI Challenge.*
