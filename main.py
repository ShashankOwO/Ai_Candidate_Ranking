from fastapi import FastAPI
from database import getdb
from routers.auth import router as auth_router
from database import Base,engine
from models.user import User
from models.candidate import Candidate


app=FastAPI()

Base.metadata.create_all(bind=engine)



app.include_router(auth_router)


@app.get("/health")
def check_health():


    return{
        "status":"running"
    }