from pydantic import BaseModel,Field

class EvaluationCriteriaCreate(BaseModel):

    criteria_name:str=Field(min_length=2,max_length=100)
    criteria_type:str=Field(pattern="^(skills|experience|qualification|projects|custom)$")
    criteria_description:str|None=None
    weight:float=Field(gt=0,le=100)
    max_score:float=Field(default=100,gt=0)