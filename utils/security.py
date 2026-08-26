from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta,timezone



pass_hash=CryptContext(
       schemes=["argon2"],
       deprecated="auto"
)

SECRET_KEY="Idk-I-GUESS"
ALGORITHM="HS256"


def hash_password(password:str):
    return pass_hash.hash(password)

def verify_password(password:str,hashed_password:str):
    return pass_hash.verify(password,hashed_password)


def create_access_token(user_id:int):
    expiry=datetime.now(timezone.utc)+timedelta(hours=1)
    pay_load={
        "user_id":user_id,
        "exp":expiry
    }
    return jwt.encode(
        pay_load,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
