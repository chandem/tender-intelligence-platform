# Tender Intelligence Platform — Backend

FastAPI backend for tender ingestion, document processing, AI analysis, contractor profiles, and requirement matching.

## Stack

- FastAPI + Uvicorn
- Pydantic Settings
- Supabase (service role)
- OpenAI (structured analysis)
- pypdf for PDF text extraction

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in SUPABASE_* and OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/api/v1/health`
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment variables

See `.env.example`:

| Variable                     | Description                          |
|------------------------------|--------------------------------------|
| `APP_NAME`                   | Service display name                 |
| `ENVIRONMENT`                | `development` / `production`         |
| `SUPABASE_URL`               | Supabase project URL                 |
| `SUPABASE_SERVICE_ROLE_KEY`  | Service role key (server only)       |
| `CORS_ORIGINS`               | Comma-separated allowed origins      |
| `OPENAI_API_KEY`             | OpenAI API key                       |
| `OPENAI_MODEL`               | Model for analysis (e.g. `gpt-4o`)   |

## Routes

All under `/api/v1`:

| Router        | Purpose                                      |
|---------------|----------------------------------------------|
| `/tenders`    | Tender CRUD                                  |
| `/documents`  | Document upload & listing                    |
| `/processing` | Processing status                            |
| `/analysis`   | AI analysis trigger & results                |
| `/contractors`| Contractor profiles                          |
| `/matches`    | Requirement matching                         |

## Project layout

```
app/
├── api/
│   ├── deps.py
│   └── routes/
├── core/config.py
├── db/supabase.py
├── schemas/
├── services/
│   ├── ai_service.py
│   ├── document_service.py
│   └── matching_service.py
└── main.py
```

## Notes

- AI responses are validated into Pydantic models before any persistence.
- Service-role key must never be exposed to the frontend.
