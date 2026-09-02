from pydantic import BaseModel
from datetime import datetime


class ProjectCreate(BaseModel):
    project_name: str
    description: str | None = None
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None


class ProjectUpdate(BaseModel):
    project_name: str | None = None
    description: str | None = None
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None


class ProjectResponse(BaseModel):
    project_id: int
    candidate_id: int
    project_name: str
    description: str | None = None
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True