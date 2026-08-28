from pydantic import BaseModel
from datetime import date


class ExperienceCreate(BaseModel):

    company_name: str
    job_title: str
    start_date: date
    end_date: date | None = None
    years: float
    description: str | None = None