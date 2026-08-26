from fastapi import FastAPI,Depends,HTTPException,APIRouter
from sqlalchemy.orm import Session

from database import getdb
from models.user import User
from schemas.user import UserCreate,UserResponse,UserLogin
from utils.security import hash_password,verify_password,create_access_token

router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",response_model=UserResponse)
def register(user_data:UserCreate,db:Session=Depends(getdb)):


    exsisting_username=(
        db.query(User).filter(User.username==user_data.username).first()
    )
    if exsisting_username:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Username already exsits"
        )

    exsisting_email=(
        db.query(User).filter(User.email==user_data.email).first()
    )
    if exsisting_email:
        db.close()
        raise HTTPException(
            status_code=400,
            detail="Email already exsits"
        )

    new_user=User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

        
 





@router.post("/login")
def login(login_data:UserLogin,db:Session=Depends(getdb)):

    user=db.query(User).filter((User.username==login_data.username_or_email)|
                               (User.email==login_data.username_or_email)).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password"
        )

    if not verify_password(login_data.password,user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password"
        )

    access_token=create_access_token(user.user_id)

    return{
        "message":"Login Successful",
        "access_token":access_token,
        "token_type":"bearer"
    }


    