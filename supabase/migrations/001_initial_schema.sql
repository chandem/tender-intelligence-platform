-- Tender Intelligence Platform — initial schema
-- Run in Supabase SQL editor or via supabase db push

-- Extensions
create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- tenders
-- ---------------------------------------------------------------------------
create table if not exists public.tenders (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 500),
  tender_number text,
  organization text,
  category text,
  location text,
  description text,
  publication_date date,
  closing_date timestamptz,
  estimated_value numeric(18,2) check (estimated_value is null or estimated_value >= 0),
  currency char(3) not null default 'ETB',
  source_url text,
  status text not null default 'new'
    check (status in ('new','processing','analyzed','reviewed','submitted','closed','cancelled')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists tenders_owner_id_idx on public.tenders(owner_id);
create index if not exists tenders_status_idx on public.tenders(status);
create index if not exists tenders_closing_date_idx on public.tenders(closing_date);

-- ---------------------------------------------------------------------------
-- tender_documents
-- ---------------------------------------------------------------------------
create table if not exists public.tender_documents (
  id uuid primary key default gen_random_uuid(),
  tender_id uuid not null references public.tenders(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  storage_path text not null,
  document_type text not null default 'tender',
  file_size bigint,
  mime_type text,
  processing_status text not null default 'uploaded'
    check (processing_status in ('uploaded','processing','extracted','failed','analyzed')),
  created_at timestamptz not null default now()
);

create index if not exists tender_documents_tender_id_idx on public.tender_documents(tender_id);
create index if not exists tender_documents_owner_id_idx on public.tender_documents(owner_id);

-- ---------------------------------------------------------------------------
-- processing_jobs
-- ---------------------------------------------------------------------------
create table if not exists public.processing_jobs (
  id uuid primary key default gen_random_uuid(),
  tender_id uuid not null references public.tenders(id) on delete cascade,
  document_id uuid not null references public.tender_documents(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  job_type text not null default 'text_extraction',
  status text not null default 'pending'
    check (status in ('pending','processing','completed','failed')),
  progress int not null default 0 check (progress between 0 and 100),
  error_message text,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists processing_jobs_document_id_idx on public.processing_jobs(document_id);

-- ---------------------------------------------------------------------------
-- tender_analyses (one row per tender)
-- ---------------------------------------------------------------------------
create table if not exists public.tender_analyses (
  id uuid primary key default gen_random_uuid(),
  tender_id uuid not null unique references public.tenders(id) on delete cascade,
  owner_id uuid not null references auth.users(id) on delete cascade,
  analysis jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- tender_requirements (flattened from AI analysis)
-- ---------------------------------------------------------------------------
create table if not exists public.tender_requirements (
  id uuid primary key default gen_random_uuid(),
  tender_id uuid not null references public.tenders(id) on delete cascade,
  requirement_type text not null,
  description text not null default '',
  required_value text,
  unit text,
  mandatory boolean not null default true,
  source_page int,
  confidence numeric(4,3) check (confidence is null or (confidence >= 0 and confidence <= 1)),
  verified boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists tender_requirements_tender_id_idx on public.tender_requirements(tender_id);

-- ---------------------------------------------------------------------------
-- contractors
-- ---------------------------------------------------------------------------
create table if not exists public.contractors (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  company_name text not null,
  license_grade text,
  business_type text,
  region text,
  city text,
  contact_email text,
  phone text,
  financial_capacity numeric(18,2),
  years_experience int check (years_experience is null or years_experience >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists contractors_owner_id_idx on public.contractors(owner_id);

-- ---------------------------------------------------------------------------
-- contractor_experience
-- ---------------------------------------------------------------------------
create table if not exists public.contractor_experience (
  id uuid primary key default gen_random_uuid(),
  contractor_id uuid not null references public.contractors(id) on delete cascade,
  project_name text not null,
  client text,
  project_type text,
  contract_value numeric(18,2),
  currency char(3) not null default 'ETB',
  location text,
  completion_year int,
  created_at timestamptz not null default now()
);

create index if not exists contractor_experience_contractor_id_idx on public.contractor_experience(contractor_id);

-- ---------------------------------------------------------------------------
-- contractor_equipment
-- ---------------------------------------------------------------------------
create table if not exists public.contractor_equipment (
  id uuid primary key default gen_random_uuid(),
  contractor_id uuid not null references public.contractors(id) on delete cascade,
  equipment_type text not null,
  quantity int not null check (quantity > 0),
  ownership text,
  condition text,
  created_at timestamptz not null default now()
);

create index if not exists contractor_equipment_contractor_id_idx on public.contractor_equipment(contractor_id);

-- ---------------------------------------------------------------------------
-- tender_matches
-- ---------------------------------------------------------------------------
create table if not exists public.tender_matches (
  id uuid primary key default gen_random_uuid(),
  tender_id uuid not null references public.tenders(id) on delete cascade,
  contractor_id uuid not null references public.contractors(id) on delete cascade,
  overall_score numeric(5,2),
  matched_count int default 0,
  partial_count int default 0,
  gap_count int default 0,
  details jsonb default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tender_id, contractor_id)
);

create index if not exists tender_matches_tender_id_idx on public.tender_matches(tender_id);

-- ---------------------------------------------------------------------------
-- updated_at trigger helper
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists tenders_set_updated_at on public.tenders;
create trigger tenders_set_updated_at
  before update on public.tenders
  for each row execute function public.set_updated_at();

drop trigger if exists tender_analyses_set_updated_at on public.tender_analyses;
create trigger tender_analyses_set_updated_at
  before update on public.tender_analyses
  for each row execute function public.set_updated_at();

drop trigger if exists contractors_set_updated_at on public.contractors;
create trigger contractors_set_updated_at
  before update on public.contractors
  for each row execute function public.set_updated_at();

drop trigger if exists tender_matches_set_updated_at on public.tender_matches;
create trigger tender_matches_set_updated_at
  before update on public.tender_matches
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
alter table public.tenders enable row level security;
alter table public.tender_documents enable row level security;
alter table public.processing_jobs enable row level security;
alter table public.tender_analyses enable row level security;
alter table public.tender_requirements enable row level security;
alter table public.contractors enable row level security;
alter table public.contractor_experience enable row level security;
alter table public.contractor_equipment enable row level security;
alter table public.tender_matches enable row level security;

-- Owner-only policies (authenticated users)
create policy "tenders_owner_all" on public.tenders
  for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

create policy "tender_documents_owner_all" on public.tender_documents
  for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

create policy "processing_jobs_owner_all" on public.processing_jobs
  for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

create policy "tender_analyses_owner_all" on public.tender_analyses
  for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

create policy "tender_requirements_via_tender" on public.tender_requirements
  for all using (
    exists (select 1 from public.tenders t where t.id = tender_id and t.owner_id = auth.uid())
  ) with check (
    exists (select 1 from public.tenders t where t.id = tender_id and t.owner_id = auth.uid())
  );

create policy "contractors_owner_all" on public.contractors
  for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);

create policy "contractor_experience_via_contractor" on public.contractor_experience
  for all using (
    exists (select 1 from public.contractors c where c.id = contractor_id and c.owner_id = auth.uid())
  ) with check (
    exists (select 1 from public.contractors c where c.id = contractor_id and c.owner_id = auth.uid())
  );

create policy "contractor_equipment_via_contractor" on public.contractor_equipment
  for all using (
    exists (select 1 from public.contractors c where c.id = contractor_id and c.owner_id = auth.uid())
  ) with check (
    exists (select 1 from public.contractors c where c.id = contractor_id and c.owner_id = auth.uid())
  );

create policy "tender_matches_via_tender" on public.tender_matches
  for all using (
    exists (select 1 from public.tenders t where t.id = tender_id and t.owner_id = auth.uid())
  ) with check (
    exists (select 1 from public.tenders t where t.id = tender_id and t.owner_id = auth.uid())
  );

-- ---------------------------------------------------------------------------
-- Storage bucket (run in dashboard or via API if preferred)
-- ---------------------------------------------------------------------------
-- insert into storage.buckets (id, name, public)
-- values ('tender-documents', 'tender-documents', false)
-- on conflict (id) do nothing;
--
-- Then add storage policies so users can only access paths under their uid:
-- (owner_id/tender_id/filename)
