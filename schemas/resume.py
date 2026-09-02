from datetime import datetime
from pydantic import BaseModel


class ResumeResponse(BaseModel):
    resume_id: int
    candidate_id: int
    candidate_name: str | None = None
    candidate_email: str | None = None
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime | None = None
    raw_text: str | None = None

    class Config:
        from_attributes = True
