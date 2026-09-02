from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers.auth import router as auth_router
from routers.candidate import router as candidate_router
from routers.chatbot import router as chatbot_router
from routers.evaluation import router as evaluation_router
from routers.job import router as job_router
from routers.job_skill import router as job_skill_router
from routers.resume import router as resume_router
from routers.skill import router as skill_router


app = FastAPI(title="AI Candidate Ranking API")

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(job_skill_router)
app.include_router(skill_router)
app.include_router(evaluation_router)
app.include_router(candidate_router)
app.include_router(chatbot_router)


@app.get("/health")
def check_health():
    return {
        "status": "running"
    }