from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    skill_name: str = Field(min_length=2, max_length=100)
    skill_category: str | None = Field(default=None, max_length=100)


class SkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str | None = None

    class Config:
        from_attributes = True


class CandidateSkillCreate(BaseModel):
    skill_id: int
    proficiency: str | None = None
    years_experience: float | int | None = None


class CandidateSkillUpdate(BaseModel):
    skill_id: int | None = None
    proficiency: str | None = None
    years_experience: float | int | None = None


class CandidateSkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str | None = None
    proficiency: str | None = None
    years_experience: float | int | None = None

    class Config:
        from_attributes = True
