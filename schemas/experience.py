from pydantic import BaseModel
from datetime import date, datetime


class ExperienceCreate(BaseModel):
    company_name: str
    job_title: str
    start_date: date | str | None = None
    end_date: date | str | None = None
    years: float | int | None = None
    description: str | None = None


class ExperienceUpdate(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    start_date: date | str | None = None
    end_date: date | str | None = None
    years: float | int | None = None
    description: str | None = None


class ExperienceResponse(BaseModel):
    experience_id: int
    candidate_id: int
    company_name: str
    job_title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    years: int | float | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True