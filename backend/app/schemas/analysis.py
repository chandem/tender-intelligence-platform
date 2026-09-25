from pydantic import BaseModel, Field

class TenderAnalysis(BaseModel):
    summary: str = ""
    tender_type: str = ""
    organization: str = ""
    location: str = ""
    closing_date: str = ""
    eligibility: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    technical_requirements: list[str] = Field(default_factory=list)
    financial_requirements: list[str] = Field(default_factory=list)
    equipment_requirements: list[str] = Field(default_factory=list)
    personnel_requirements: list[str] = Field(default_factory=list)
    important_dates: list[str] = Field(default_factory=list)
    risks_or_missing_information: list[str] = Field(default_factory=list)
