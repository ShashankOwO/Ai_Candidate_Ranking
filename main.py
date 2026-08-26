from fastapi import FastAPI
from database import getdb
from routers.auth import router as auth_router
from routers.resume import router as resume_router
from routers.job import router as job_router
import models
from database import Base,engine


app=FastAPI()

Base.metadata.create_all(bind=engine)



app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)


@app.get("/health")
def check_health():


    return{
        "status":"running"
    }