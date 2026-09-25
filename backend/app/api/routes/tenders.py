from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.schemas.tender import TenderCreate, TenderResponse, TenderUpdate

router = APIRouter(prefix="/tenders", tags=["tenders"])

def _get_tender(tender_id: str, owner_id: str):
    result = supabase.table("tenders").select("*").eq("id", tender_id).eq("owner_id", owner_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Tender not found")
    return result.data

@router.get("", response_model=list[TenderResponse])
def list_tenders(owner_id: str = Depends(get_current_user_id)):
    return supabase.table("tenders").select("*").eq("owner_id", owner_id).order("created_at", desc=True).execute().data

@router.post("", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
def create_tender(payload: TenderCreate, owner_id: str = Depends(get_current_user_id)):
    data = payload.model_dump(mode="json")
    data["owner_id"] = owner_id
    result = supabase.table("tenders").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create tender")
    return result.data[0]

@router.get("/{tender_id}", response_model=TenderResponse)
def get_tender(tender_id: str, owner_id: str = Depends(get_current_user_id)):
    return _get_tender(tender_id, owner_id)

@router.patch("/{tender_id}", response_model=TenderResponse)
def update_tender(tender_id: str, payload: TenderUpdate, owner_id: str = Depends(get_current_user_id)):
    _get_tender(tender_id, owner_id)
    updates = {k: v for k, v in payload.model_dump(mode="json").items() if v is not None}
    if not updates:
        return _get_tender(tender_id, owner_id)
    result = supabase.table("tenders").update(updates).eq("id", tender_id).eq("owner_id", owner_id).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update tender")
    return result.data[0]

@router.delete("/{tender_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tender(tender_id: str, owner_id: str = Depends(get_current_user_id)):
    _get_tender(tender_id, owner_id)
    supabase.table("tenders").delete().eq("id", tender_id).eq("owner_id", owner_id).execute()
