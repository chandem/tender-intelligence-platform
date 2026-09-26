-- Align tender_matches with fields produced by matching_service.build_match

alter table public.tender_matches
  add column if not exists license_match boolean,
  add column if not exists experience_match boolean,
  add column if not exists equipment_match boolean,
  add column if not exists financial_match boolean,
  add column if not exists deadline_status text,
  add column if not exists missing_requirements jsonb default '[]'::jsonb,
  add column if not exists match_details jsonb default '[]'::jsonb,
  add column if not exists notes text;

-- Keep overall_score / counts optional for future scoring rollups
