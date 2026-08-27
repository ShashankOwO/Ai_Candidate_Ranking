from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.job import Job, JobSkill
from models.skill import Skill
from models.user import User
from utils.auth import get_current_user
from schemas.job_skill import JobSkillCreate


router = APIRouter(
    prefix="/jobs",
    tags=["Job Skills"]
)


@router.post("/{job_id}/skills")
def add_job_skill(
    job_id: int,
    skill_data: JobSkillCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(Job)
        .filter(
            Job.job_id == job_id,
            Job.user_id == current_user.user_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )


    skill = (
        db.query(Skill)
        .filter(Skill.skill_id == skill_data.skill_id)
        .first()
    )

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

   
    existing = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_data.skill_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Skill already added to this job"
        )

  
    job_skill = JobSkill(
        job_id=job_id,
        skill_id=skill_data.skill_id,
        skill_type=skill_data.skill_type
    )

    db.add(job_skill)
    db.commit()

    return {
        "message": "Skill added to job",
        "job_id": job_id,
        "skill_id": skill_data.skill_id,
        "skill_name": skill.skill_name,
        "skill_type": skill_data.skill_type
    }