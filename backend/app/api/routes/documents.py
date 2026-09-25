from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.schemas.document import DocumentResponse, ProcessingJobResponse

router = APIRouter(prefix="/tenders/{tender_id}/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(tender_id: UUID, file: UploadFile = File(...), owner_id: str = Depends(get_current_user_id)):
    tender = supabase.table("tenders").select("id").eq("id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not tender.data:
        raise HTTPException(status_code=404, detail="Tender not found")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be 25 MB or smaller")
    path = f"{owner_id}/{tender_id}/{file.filename}"
    try:
        supabase.storage.from_("tender-documents").upload(path, content, {"content-type": "application/pdf", "upsert": "true"})
        doc = supabase.table("tender_documents").insert({
            "tender_id": str(tender_id), "owner_id": owner_id, "file_name": file.filename or "document.pdf",
            "storage_path": path, "document_type": "tender", "file_size": len(content),
            "mime_type": "application/pdf", "processing_status": "uploaded"
        }).execute()
        if not doc.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        return doc.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to upload document") from exc

@router.get("", response_model=list[DocumentResponse])
def list_documents(tender_id: UUID, owner_id: str = Depends(get_current_user_id)):
    result = supabase.table("tender_documents").select("*").eq("tender_id", str(tender_id)).eq("owner_id", owner_id).order("created_at", desc=True).execute()
    return result.data

@router.get("/{document_id}/job", response_model=ProcessingJobResponse)
def get_processing_job(tender_id: UUID, document_id: UUID, owner_id: str = Depends(get_current_user_id)):
    result = supabase.table("processing_jobs").select("*").eq("tender_id", str(tender_id)).eq("document_id", str(document_id)).eq("owner_id", owner_id).order("created_at", desc=True).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return result.data[0]
