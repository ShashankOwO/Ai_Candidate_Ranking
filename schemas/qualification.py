from pydantic import BaseModel
from datetime import datetime


class QualificationCreate(BaseModel):
    university: str | None = None
    degree: str | None = None
    specialization: str | None = None
    percentage: float | None = None
    passed_out_year: int | None = None
    joining_year: int | None = None


class QualificationUpdate(BaseModel):
    university: str | None = None
    degree: str | None = None
    specialization: str | None = None
    percentage: float | None = None
    passed_out_year: int | None = None
    joining_year: int | None = None


class QualificationResponse(BaseModel):
    qualification_id: int
    candidate_id: int
    university: str | None = None
    degree: str | None = None
    specialization: str | None = None
    percentage: float | None = None
    passed_out_year: int | None = None
    joining_year: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True