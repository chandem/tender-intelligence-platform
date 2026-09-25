from openai import OpenAI
from app.core.config import settings
from app.schemas.analysis import TenderAnalysis

SYSTEM_PROMPT = """You are a tender intelligence analyst. Analyze procurement/tender text conservatively. Extract only information supported by the document. Do not invent requirements, dates, amounts, eligibility rules, or facts. Put uncertain or absent information in risks_or_missing_information. Return structured data matching the requested schema."""

def analyze_tender_text(text: str) -> TenderAnalysis:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:120000]},
        ],
        text_format=TenderAnalysis,
    )
    if response.output_parsed is None:
        raise RuntimeError("AI returned no structured analysis")
    return response.output_parsed
