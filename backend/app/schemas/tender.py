from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

TenderStatus = Literal["new","processing","analyzed","reviewed","submitted","closed","cancelled"]

class TenderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    tender_number: str | None = None
    organization: str | None = None
    category: str | None = None
    location: str | None = None
    description: str | None = None
    publication_date: date | None = None
    closing_date: datetime | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="ETB", min_length=3, max_length=3)
    source_url: HttpUrl | None = None

class TenderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    tender_number: str | None = None
    organization: str | None = None
    category: str | None = None
    location: str | None = None
    description: str | None = None
    publication_date: date | None = None
    closing_date: datetime | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    source_url: HttpUrl | None = None
    status: TenderStatus | None = None

class TenderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    title: str
    tender_number: str | None = None
    organization: str | None = None
    category: str | None = None
    location: str | None = None
    description: str | None = None
    publication_date: date | None = None
    closing_date: datetime | None = None
    estimated_value: Decimal | None = None
    currency: str
    source_url: str | None = None
    status: TenderStatus
    created_at: datetime
    updated_at: datetime
