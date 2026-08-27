from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import getdb
from models.job import Job
from schemas.job import JobCreate,JobResponse
from utils.auth import get_current_user
from models.user import User

router=APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)



@router.post("/",response_model=JobResponse)
def create_job(
    job_data:JobCreate,
    db:Session=Depends(getdb),
    current_user:User=Depends(get_current_user)
):
    new_job=Job(
        user_id=current_user.user_id,
        job_title=job_data.job_title,
        job_description=job_data.job_description,
        minimum_experience=job_data.minimum_experience
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


