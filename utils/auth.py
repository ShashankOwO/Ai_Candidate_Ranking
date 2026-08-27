from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt,JWTError
from sqlalchemy.orm import Session

from database import getdb
from models.user import User
from utils.security import SECRET_KEY,ALGORITHM


security=HTTPBearer()

def get_current_user(
        credentials:HTTPAuthorizationCredentials=Depends(security),
        db:Session=Depends(getdb)
):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldnot validate credentials.",
        headers={
            "WWW-Authenticate":"Bearer"
        }
    )
    token=credentials.credentials

    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id=payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user=db.query(User).filter(User.user_id==user_id).first()

    if user is None:
        raise credentials_exception

    return user


