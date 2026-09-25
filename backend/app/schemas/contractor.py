from uuid import UUID
from pydantic import BaseModel, Field

class ContractorCreate(BaseModel):
    company_name: str
    license_grade: str | None = None
    business_type: str | None = None
    region: str | None = None
    city: str | None = None
    contact_email: str | None = None
    phone: str | None = None
    financial_capacity: float | None = None
    years_experience: int | None = Field(default=None, ge=0)

class ContractorResponse(ContractorCreate):
    id: UUID
    owner_id: UUID

class ExperienceCreate(BaseModel):
    project_name: str
    client: str | None = None
    project_type: str | None = None
    contract_value: float | None = None
    currency: str = "ETB"
    location: str | None = None
    completion_year: int | None = None

class EquipmentCreate(BaseModel):
    equipment_type: str
    quantity: int = Field(gt=0)
    ownership: str | None = None
    condition: str | None = None
