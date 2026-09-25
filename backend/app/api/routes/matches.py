from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.services.matching_service import build_match

router = APIRouter(prefix="/matches", tags=["matches"])

@router.post("/{tender_id}/{contractor_id}")
def match_tender(tender_id: UUID, contractor_id: UUID, owner_id: str = Depends(get_current_user_id)):
    tender = supabase.table("tenders").select("*").eq("id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    contractor = supabase.table("contractors").select("*").eq("id", str(contractor_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not tender.data or not contractor.data:
        raise HTTPException(status_code=404, detail="Tender or contractor not found")
    requirements = supabase.table("tender_requirements").select("*").eq("tender_id", str(tender_id)).execute().data
    experience = supabase.table("contractor_experience").select("*").eq("contractor_id", str(contractor_id)).execute().data
    equipment = supabase.table("contractor_equipment").select("*").eq("contractor_id", str(contractor_id)).execute().data
    match = build_match(tender.data, requirements, contractor.data, experience, equipment)
    row = {"tender_id": str(tender_id), "contractor_id": str(contractor_id), **match}
    result = supabase.table("tender_matches").upsert(row, on_conflict="tender_id,contractor_id").execute()
    return result.data[0] if result.data else row

@router.get("/{tender_id}")
def list_matches(tender_id: UUID, owner_id: str = Depends(get_current_user_id)):
    tender = supabase.table("tenders").select("id").eq("id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not tender.data:
        raise HTTPException(status_code=404, detail="Tender not found")
    return supabase.table("tender_matches").select("*").eq("tender_id", str(tender_id)).order("created_at", desc=True).execute().data
