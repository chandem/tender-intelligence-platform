# Architecture

## Product flow

**Find → Understand → Filter → Match → Prepare → Track**

1. **Find** – Ingest or create tender opportunities.
2. **Understand** – Upload documents, extract text, run AI analysis into structured fields.
3. **Filter** – Review eligibility, requirements, risks, and deadlines.
4. **Match** – Compare contractor capabilities against tender requirements.
5. **Prepare** – Identify gaps and required documents for submission.
6. **Track** – Monitor status and closing dates.

## MVP user flow

1. User signs in (Supabase Auth).
2. User creates a tender record.
3. User uploads a tender PDF.
4. Backend records processing status.
5. Text extraction + AI analysis produce structured results (validated via Pydantic schemas).
6. User reviews requirements and verifies important fields.
7. Contractor profile is matched requirement-by-requirement.

## Stack

| Layer              | Choice                          | Notes                                      |
|--------------------|---------------------------------|--------------------------------------------|
| Frontend           | React 19 + Vite + TypeScript    | SPA, talks to FastAPI + Supabase           |
| Backend            | FastAPI + Python                | REST API under `/api/v1`                   |
| Database / Auth / Storage | Supabase                   | PostgreSQL + Auth + Storage; RLS required  |
| AI                 | OpenAI structured outputs       | Analysis validated into schemas            |
| Deployment         | Vercel (frontend) + Render (backend) |                                      |

## Backend layout

```
backend/app/
├── api/routes/       # HTTP endpoints (tenders, documents, processing, analysis, contractors, matches)
├── core/             # Settings (pydantic-settings)
├── db/               # Supabase client (service role)
├── schemas/          # Pydantic models for requests/responses and AI output
├── services/         # Business logic (AI, document processing, matching)
└── main.py           # App factory, CORS, router registration
```

## Design principles

- **AI is not a database writer.** Analysis results are parsed into strict schemas (`TenderAnalysis`, etc.) and only then persisted by application code.
- **Service-role keys stay server-side.** Frontend uses the anon key + user JWT; backend uses the service role when needed.
- **Row Level Security (RLS)** must be enabled on all tables exposed to clients.
- **CORS** is restricted via `CORS_ORIGINS` (default `http://localhost:5173`).
- **Conservative extraction.** The AI system prompt instructs the model not to invent requirements, dates, or eligibility rules.

## API surface (high level)

| Module       | Purpose                                      |
|--------------|----------------------------------------------|
| `/tenders`   | CRUD for tender records                      |
| `/documents` | Upload and manage tender documents           |
| `/processing`| Track document processing status             |
| `/analysis`  | Trigger / retrieve AI analysis results       |
| `/contractors` | Contractor capability profiles             |
| `/matches`   | Requirement-level matching results           |

Interactive docs: `GET /docs` when the API is running.

## Future considerations

- Database migrations and storage policies under `supabase/`
- Background jobs for heavy document processing
- Webhooks / notifications for closing dates
- Multi-tenant org support and richer RBAC
