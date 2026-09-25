from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.services.document_service import process_document

router = APIRouter(prefix="/documents", tags=["processing"])

def run_processing(document_id: str, owner_id: str):
    try:
        process_document(document_id, owner_id)
    except Exception:
        pass

@router.post("/{document_id}/process")
def start_processing(document_id: UUID, background_tasks: BackgroundTasks, owner_id: str = Depends(get_current_user_id)):
    result = supabase.table("tender_documents").select("id").eq("id", str(document_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")
    background_tasks.add_task(run_processing, str(document_id), owner_id)
    return {"document_id": str(document_id), "status": "queued"}
