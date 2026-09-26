# Supabase

Database schema, migrations, and storage policies for Tender Intelligence Platform.

## Principles

- **Row Level Security (RLS)** is enabled on all application tables.
- **Service-role credentials** are used only by the FastAPI backend — never in the browser.
- Frontend uses the **anon key** + authenticated user JWT.

## Migrations

| File | Description |
|------|-------------|
| [`migrations/001_initial_schema.sql`](migrations/001_initial_schema.sql) | Core tables, indexes, triggers, RLS policies |
| [`migrations/002_align_tender_matches.sql`](migrations/002_align_tender_matches.sql) | Extra columns for match service output |

### Apply

1. Open your Supabase project → **SQL Editor**
2. Paste and run `001_initial_schema.sql`
3. Then run `002_align_tender_matches.sql`

Or use the Supabase CLI:

```bash
supabase db push
```

## Tables

| Table | Purpose |
|-------|--------|
| `tenders` | Core tender records |
| `tender_documents` | Uploaded PDFs (metadata + storage path) |
| `processing_jobs` | Text extraction job status |
| `tender_analyses` | Full AI analysis JSON (one per tender) |
| `tender_requirements` | Flattened requirements for matching |
| `contractors` | Contractor / company profiles |
| `contractor_experience` | Past projects |
| `contractor_equipment` | Equipment inventory |
| `tender_matches` | Requirement-level match results |

## Storage bucket

Create a **private** bucket named `tender-documents`:

1. Supabase Dashboard → **Storage** → New bucket → `tender-documents` (private)
2. Suggested path layout: `{owner_id}/{tender_id}/{filename}`

Example storage policies (adjust as needed):

```sql
-- Allow authenticated users to upload under their own uid prefix
create policy "Users upload own tender docs"
on storage.objects for insert to authenticated
with check (
  bucket_id = 'tender-documents'
  and (storage.foldername(name))[1] = auth.uid()::text
);

create policy "Users read own tender docs"
on storage.objects for select to authenticated
using (
  bucket_id = 'tender-documents'
  and (storage.foldername(name))[1] = auth.uid()::text
);
```

Backend uses the **service role** and can read/write all objects; these policies protect direct client access.

## Environment

**Backend** (`backend/.env`):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Frontend** (`frontend/.env`):

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```
