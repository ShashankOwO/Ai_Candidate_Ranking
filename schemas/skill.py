from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    skill_name: str = Field(min_length=2,max_length=100)

    skill_category: str | None = Field(default=None,max_length=100)


class SkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str | None

    class Config:
        from_attributes = True