from pydantic import BaseModel, Field

class ExtractedRequirement(BaseModel):
    description: str = ""
    required_value: str = ""
    unit: str = ""
    mandatory: bool = True
    source_page: int | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

class TenderAnalysis(BaseModel):
    summary: str = ""
    tender_type: str = ""
    organization: str = ""
    location: str = ""
    closing_date: str = ""
    experience_requirements: list[ExtractedRequirement] = Field(default_factory=list)\n    eligibility: list[ExtractedRequirement] = Field(default_factory=list)
    required_documents: list[ExtractedRequirement] = Field(default_factory=list)
    technical_requirements: list[ExtractedRequirement] = Field(default_factory=list)
    financial_requirements: list[ExtractedRequirement] = Field(default_factory=list)
    equipment_requirements: list[ExtractedRequirement] = Field(default_factory=list)
    personnel_requirements: list[ExtractedRequirement] = Field(default_factory=list)
    important_dates: list[ExtractedRequirement] = Field(default_factory=list)
    risks_or_missing_information: list[str] = Field(default_factory=list)
