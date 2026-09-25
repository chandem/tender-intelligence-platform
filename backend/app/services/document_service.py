from io import BytesIO
from pypdf import PdfReader
from app.db.supabase import supabase

def extract_pdf_text(content: bytes) -> tuple[str, int]:
    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n\n".join(pages).strip(), len(reader.pages)

def process_document(document_id: str, owner_id: str) -> dict:
    doc_result = supabase.table("tender_documents").select("*").eq("id", document_id).eq("owner_id", owner_id).maybe_single().execute()
    if not doc_result.data:
        raise ValueError("Document not found")
    doc = doc_result.data
    job = supabase.table("processing_jobs").insert({
        "tender_id": doc["tender_id"], "document_id": document_id, "owner_id": owner_id,
        "job_type": "text_extraction", "status": "processing", "progress": 10
    }).execute()
    job_data = job.data[0]
    try:
        supabase.table("tender_documents").update({"processing_status": "processing"}).eq("id", document_id).eq("owner_id", owner_id).execute()
        stored = supabase.storage.from_("tender-documents").download(doc["storage_path"])
        text, page_count = extract_pdf_text(stored)
        if not text:
            raise ValueError("No selectable text found. This PDF may require OCR.")
        supabase.table("tender_documents").update({"processing_status": "extracted"}).eq("id", document_id).eq("owner_id", owner_id).execute()
        supabase.table("processing_jobs").update({"status": "completed", "progress": 100, "completed_at": "now()"}).eq("id", job_data["id"]).execute()
        return {"document_id": document_id, "job_id": job_data["id"], "page_count": page_count, "character_count": len(text), "text": text}
    except Exception as exc:
        supabase.table("tender_documents").update({"processing_status": "failed"}).eq("id", document_id).eq("owner_id", owner_id).execute()
        supabase.table("processing_jobs").update({"status": "failed", "progress": 0, "error_message": str(exc)}).eq("id", job_data["id"]).execute()
        raise
