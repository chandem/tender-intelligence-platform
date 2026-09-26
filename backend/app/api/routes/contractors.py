from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.schemas.contractor import ContractorCreate, ContractorResponse, ExperienceCreate, EquipmentCreate

router = APIRouter(prefix="/contractors", tags=["contractors"])

def owned_contractor(contractor_id: UUID, owner_id: str):
    result = supabase.table("contractors").select("*").eq("id", str(contractor_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Contractor profile not found")
    return result.data

@router.get("/me", response_model=list[ContractorResponse])
def list_my_contractors(owner_id: str = Depends(get_current_user_id)):
    return supabase.table("contractors").select("*").eq("owner_id", owner_id).order("created_at", desc=True).execute().data

@router.post("/me", response_model=ContractorResponse, status_code=201)
def create_contractor(payload: ContractorCreate, owner_id: str = Depends(get_current_user_id)):
    data = payload.model_dump(exclude_none=True) | {"owner_id": owner_id}
    result = supabase.table("contractors").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create contractor profile")
    return result.data[0]

@router.patch("/{contractor_id}", response_model=ContractorResponse)
def update_contractor(contractor_id: UUID, payload: ContractorCreate, owner_id: str = Depends(get_current_user_id)):
    owned_contractor(contractor_id, owner_id)
    data = payload.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="No profile fields supplied")
    result = supabase.table("contractors").update(data).eq("id", str(contractor_id)).eq("owner_id", owner_id).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update contractor profile")
    return result.data[0]

@router.get("/{contractor_id}")
def get_contractor(contractor_id: UUID, owner_id: str = Depends(get_current_user_id)):
    contractor = owned_contractor(contractor_id, owner_id)
    experience = supabase.table("contractor_experience").select("*").eq("contractor_id", str(contractor_id)).order("completion_year", desc=True).execute().data
    equipment = supabase.table("contractor_equipment").select("*").eq("contractor_id", str(contractor_id)).order("equipment_type").execute().data
    return {"contractor": contractor, "experience": experience, "equipment": equipment}

@router.post("/{contractor_id}/experience", status_code=201)
def add_experience(contractor_id: UUID, payload: ExperienceCreate, owner_id: str = Depends(get_current_user_id)):
    owned_contractor(contractor_id, owner_id)
    result = supabase.table("contractor_experience").insert(payload.model_dump(exclude_none=True) | {"contractor_id": str(contractor_id)}).execute()
    return result.data[0]

@router.post("/{contractor_id}/equipment", status_code=201)
def add_equipment(contractor_id: UUID, payload: EquipmentCreate, owner_id: str = Depends(get_current_user_id)):
    owned_contractor(contractor_id, owner_id)
    result = supabase.table("contractor_equipment").insert(payload.model_dump(exclude_none=True) | {"contractor_id": str(contractor_id)}).execute()
    return result.data[0]
