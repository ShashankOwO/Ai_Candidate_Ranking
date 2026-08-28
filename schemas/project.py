from pydantic import BaseModel


class ProjectCreate(BaseModel):

    project_name: str
    description: str | None = None
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None