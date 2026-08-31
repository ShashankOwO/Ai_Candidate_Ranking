from pydantic import BaseModel


class ProjectCreate(BaseModel):

    project_name: str
    description: str | None = None
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None



class ProjectResponse(BaseModel):
    project_id: int
    candidate_id: int
    project_name: str
    description: str
    technologies: str | None = None
    role: str | None = None
    duration: str | None = None

    