from pydantic import BaseModel,Field

class JobCreate(BaseModel):
    job_title:str=Field(min_length=2,max_length=150)
    job_description:str=Field(min_length=10)
    minimum_experience:int|None=Field(default=None,ge=0)


class JobResponse(BaseModel):
    job_id:int
    user_id:int
    job_title:str
    job_description:str
    minimum_experience:int|None

    class Config:
        from_attributes=True