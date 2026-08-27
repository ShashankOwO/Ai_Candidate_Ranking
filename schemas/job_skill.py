from pydantic import BaseModel, Field


class JobSkillCreate(BaseModel):
    skill_id: int

    skill_type: str = Field(pattern="^(required|preferred)$")