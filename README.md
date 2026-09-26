# Tender Intelligence Platform

AI-powered platform for discovering, analyzing, matching, and tracking tenders (RFPs, RFQs, and procurement opportunities).

**Flow:** Find → Understand → Filter → Match → Prepare → Track

## Features

- **Tender management** – Create and track tender records
- **Document intelligence** – Upload PDFs, extract text, and process documents
- **AI analysis** – Structured extraction of requirements, eligibility, dates, risks, and more
- **Contractor profiles** – Maintain capability profiles
- **Requirement matching** – Match contractor capabilities against tender requirements
- **Auth & storage** – Supabase for authentication, database, and file storage

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | React 19 + Vite + TypeScript        |
| Backend      | FastAPI + Python                    |
| Database/Auth/Storage | Supabase (PostgreSQL + Auth + Storage) |
| AI           | OpenAI (structured outputs)         |
| Deployment   | Vercel (frontend) + Render (backend) |

## Project Structure

```
tender-intelligence-platform/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/routes/      # tenders, documents, processing, analysis, contractors, matches
│   │   ├── core/            # Settings & config
│   │   ├── db/              # Supabase client
│   │   ├── schemas/         # Pydantic models
│   │   ├── services/        # AI, document, matching services
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── ...
│   └── package.json
├── docs/
│   └── architecture.md
├── supabase/                # Migrations & policies (planned)
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Supabase project
- An OpenAI API key

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials
uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/api/v1/health`
- Interactive docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
# Optional: create .env with VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

App runs at `http://localhost:5173` by default.

### 3. Environment Variables

**Backend** (`backend/.env`):

```env
APP_NAME=Tender Intelligence Platform API
ENVIRONMENT=development
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
CORS_ORIGINS=http://localhost:5173
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o   # or your preferred model
```

**Frontend** (optional `frontend/.env`):

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## API Overview

| Area          | Prefix / routes                                      |
|---------------|------------------------------------------------------|
| Health        | `GET /api/v1/health`                                 |
| Tenders       | `/api/v1/tenders`                                    |
| Documents     | `/api/v1/documents`                                  |
| Processing    | `/api/v1/processing`                                 |
| Analysis      | `/api/v1/analysis`                                   |
| Contractors   | `/api/v1/contractors`                                |
| Matches       | `/api/v1/matches`                                    |

Full interactive documentation is available at `/docs` when the backend is running.

## Architecture Notes

See [docs/architecture.md](docs/architecture.md) for product flow and design principles.

Key principles:
- AI output is validated into structured Pydantic schemas before persistence.
- Service-role Supabase credentials stay server-side only.
- Row Level Security (RLS) should be enabled on all exposed tables.

## License

Private project. License to be determined.

---

Built by [chandem](https://github.com/chandem)
