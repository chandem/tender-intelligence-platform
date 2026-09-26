# Contributing

Thanks for interest in Tender Intelligence Platform.

## Development setup

1. Clone the repo and follow the root [README](README.md).
2. Apply Supabase migrations under `supabase/migrations/`.
3. Create the private Storage bucket `tender-documents`.
4. Copy env examples and fill in credentials:
   - `backend/.env.example` → `backend/.env`
   - `frontend/.env.example` → `frontend/.env`

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Conventions

- **AI output** must be validated through Pydantic schemas before persistence.
- **Service-role** Supabase keys stay on the server only.
- Prefer small, focused PRs with a clear description.
- Keep RLS enabled on new tables; owner-scoped access is the default.

## Suggested next improvements

- OCR fallback for scanned PDFs
- Background worker (Celery / ARQ) instead of FastAPI BackgroundTasks for heavy jobs
- Org/multi-tenant support
- CI (lint + typecheck + tests)
- Deployment configs for Vercel + Render
