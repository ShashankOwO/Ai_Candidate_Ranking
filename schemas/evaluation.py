from pydantic import BaseModel,Field
from datetime import datetime
from pydantic import BaseModel, Field

class EvaluationCriteriaCreate(BaseModel):

    criteria_name:str=Field(min_length=2,max_length=100)
    criteria_type:str=Field(pattern="^(skills|experience|qualification|projects|custom)$")
    criteria_description:str|None=None
    weight:float=Field(gt=0,le=100)
    max_score:float=Field(default=100,gt=0)



    class EvaluationRunResponse(BaseModel):

     evaluation_run_id: int
     job_id: int
     created_at: datetime


class EvaluationResultResponse(BaseModel):

    evaluation_result_id: int
    evaluation_run_id: int
    candidate_id: int
    score: float
    status: str


class CandidateRankingResponse(BaseModel):

    ranking_id: int
    evaluation_run_id: int
    candidate_id: int
    rank: int
    score: float


class EvaluationRunListResponse(BaseModel):

    evaluation_run_id: int
    job_id: int
    created_at: datetime


class CandidateEvaluationResponse(BaseModel):

    evaluation_run_id: int
    candidate_id: int
    score: float
    status: str
    rank: int | None = None






class EvaluationCriteriaUpdate(BaseModel):

    criteria_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    criteria_type: str | None = Field(
        default=None,
        pattern="^(skills|experience|qualification|projects|custom)$"
    )

    criteria_description: str | None = None

    weight: float | None = Field(
        default=None,
        gt=0,
        le=100
    )

    max_score: float | None = Field(
        default=None,
        gt=0
    )