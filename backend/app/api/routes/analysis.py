from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.services.document_service import process_document
from app.services.ai_service import analyze_tender_text

router = APIRouter(prefix="/tenders/{tender_id}/analysis", tags=["analysis"])

@router.post("")
def analyze_tender(tender_id: UUID, owner_id: str = Depends(get_current_user_id)):
    tender = supabase.table("tenders").select("id").eq("id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not tender.data:
        raise HTTPException(status_code=404, detail="Tender not found")
    docs = supabase.table("tender_documents").select("*").eq("tender_id", str(tender_id)).eq("owner_id", owner_id).order("created_at", desc=True).limit(1).execute()
    if not docs.data:
        raise HTTPException(status_code=400, detail="Upload a tender PDF first")
    doc = docs.data[0]
    try:
        extracted = process_document(doc["id"], owner_id)
        analysis = analyze_tender_text(extracted["text"])
        rows = []
        groups = {
            "eligibility": analysis.eligibility,
            "document": analysis.required_documents,
            "technical": analysis.technical_requirements,
            "financial": analysis.financial_requirements,
            "equipment": analysis.equipment_requirements,
            "personnel": analysis.personnel_requirements,
            "date": analysis.important_dates,
        }
        for requirement_type, items in groups.items():
            for item in items:
                rows.append({"tender_id": str(tender_id), "requirement_type": requirement_type, "description": item, "mandatory": True, "verified": False})
        if rows:
            supabase.table("tender_requirements").delete().eq("tender_id", str(tender_id)).execute()
            supabase.table("tender_requirements").insert(rows).execute()
        supabase.table("tenders").update({"status": "analyzed"}).eq("id", str(tender_id)).eq("owner_id", owner_id).execute()
        return {"tender_id": str(tender_id), "analysis": analysis.model_dump(), "requirements_created": len(rows)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Tender analysis failed") from exc
