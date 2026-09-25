from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user_id
from app.db.supabase import supabase
from app.services.document_service import process_document
from app.services.ai_service import analyze_tender_text

router = APIRouter(prefix="/tenders/{tender_id}/analysis", tags=["analysis"])


def _get_tender(tender_id: UUID, owner_id: str):
    result = supabase.table("tenders").select("id").eq("id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Tender not found")


@router.get("")
def get_analysis(tender_id: UUID, owner_id: str = Depends(get_current_user_id)):
    _get_tender(tender_id, owner_id)
    result = supabase.table("tender_analyses").select("analysis,created_at,updated_at").eq("tender_id", str(tender_id)).eq("owner_id", owner_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No AI analysis found")
    return {"tender_id": str(tender_id), "analysis": result.data["analysis"], "created_at": result.data["created_at"], "updated_at": result.data["updated_at"]}


@router.post("")
def analyze_tender(tender_id: UUID, owner_id: str = Depends(get_current_user_id)):
    _get_tender(tender_id, owner_id)
    docs = supabase.table("tender_documents").select("*").eq("tender_id", str(tender_id)).eq("owner_id", owner_id).order("created_at", desc=True).limit(1).execute()
    if not docs.data:
        raise HTTPException(status_code=400, detail="Upload a tender PDF first")
    doc = docs.data[0]
    try:
        extracted = process_document(doc["id"], owner_id)
        analysis = analyze_tender_text(extracted["text"])
        analysis_data = analysis.model_dump()

        supabase.table("tender_analyses").upsert({
            "tender_id": str(tender_id),
            "owner_id": owner_id,
            "analysis": analysis_data,
            "updated_at": "now()",
        }, on_conflict="tender_id").execute()

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
                rows.append({
                    "tender_id": str(tender_id),
                    "requirement_type": requirement_type,
                    "description": item,
                    "mandatory": True,
                    "verified": False,
                })
        supabase.table("tender_requirements").delete().eq("tender_id", str(tender_id)).execute()
        if rows:
            supabase.table("tender_requirements").insert(rows).execute()
        supabase.table("tenders").update({"status": "analyzed"}).eq("id", str(tender_id)).eq("owner_id", owner_id).execute()
        return {"tender_id": str(tender_id), "analysis": analysis_data, "requirements_created": len(rows)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Tender analysis failed") from exc
