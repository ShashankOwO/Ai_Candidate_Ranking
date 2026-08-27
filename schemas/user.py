from pydantic import BaseModel,EmailStr,Field


class UserCreate(BaseModel):
    username:str=Field(min_length=3,max_length=50)
    email:EmailStr
    password:str=Field(min_length=8,max_length=72)



class UserResponse(BaseModel):
    user_id:int
    username:str
    email:str

    class Config:
        from_attributes=True



class UserLogin(BaseModel):
    username_or_email:str
    password:str



    