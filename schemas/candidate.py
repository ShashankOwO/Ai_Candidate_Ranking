from pydantic import BaseModel, EmailStr, Field
 
 
class CandidateCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100
    )
 
    contact_no: str | None = Field(
        default=None,
        max_length=20
    )
 
    email_address: EmailStr | None = None
 
 
class CandidateResponse(BaseModel):
    candidate_id: int
    user_id: int
    full_name: str
    contact_no: str | None
    email_address: str | None
 
    class Config:
        from_attributes = True