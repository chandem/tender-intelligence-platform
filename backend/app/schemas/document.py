from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: UUID
    tender_id: UUID
    owner_id: UUID
    file_name: str
    storage_path: str
    document_type: str
    file_size: int | None = None
    mime_type: str | None = None
    processing_status: str
    created_at: datetime

class ProcessingJobResponse(BaseModel):
    id: UUID
    tender_id: UUID
    document_id: UUID
    owner_id: UUID
    job_type: str
    status: str
    progress: int
    error_message: str | None = None
    created_at: datetime
