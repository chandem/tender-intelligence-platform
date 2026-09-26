# Supabase

Database schema, migrations, and storage policies for Tender Intelligence Platform live here.

## Principles

- **Row Level Security (RLS)** must be enabled on all application tables exposed to clients.
- **Service-role credentials** are used only by the FastAPI backend and must never be shipped to the browser.
- Frontend uses the **anon key** + authenticated user JWT.

## Suggested tables (MVP)

| Table              | Purpose                                              |
|--------------------|------------------------------------------------------|
| `tenders`          | Core tender records (title, org, location, status, closing_date, …) |
| `documents`        | Uploaded files linked to tenders (storage path, status) |
| `analyses`         | Structured AI analysis results                       |
| `contractors`      | Contractor / company capability profiles             |
| `matches`          | Requirement-level match results between contractors and tenders |

Exact columns should follow the Pydantic schemas in `backend/app/schemas/`.

## Setup checklist

1. Create a Supabase project.
2. Enable Auth (email or preferred providers).
3. Create tables with RLS policies (users can only access their own rows or org-scoped rows).
4. Create a Storage bucket for tender PDFs; restrict uploads/downloads via policies.
5. Copy project URL + keys into:
   - `backend/.env` → `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
   - `frontend/.env` → `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`

## Migrations

Add SQL migration files in this directory (or use the Supabase CLI) as the schema evolves.
