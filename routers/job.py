from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import getdb
from models.job import Job
from schemas.job import JobCreate,JobResponse
from utils.auth import get_current_user
from models.user import User
from models.job import Job, JobSkill
from models.skill import Skill
from models.evaluation import EvaluationCriteria
from fastapi import HTTPException

router=APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)



@router.post("/create",response_model=JobResponse)
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





@router.get("/all")
def get_jobs(
    db:Session=Depends(getdb),
    current_user:User=Depends(get_current_user)
):
    jobs=db.query(Job).filter(Job.user_id==current_user.user_id).all()

    return jobs



@router.get("/{job_id}")
def get_job(
    job_id:int,
    db:Session=Depends(getdb),
    current_user:User=Depends(get_current_user)
):
    job=db.query(Job).filter(Job.job_id==job_id,Job.user_id==current_user.user_id).first()

    if not job:
        raise HTTPException(status_code=404,detail="Job not found")


    skills = (
        db.query(JobSkill, Skill)
        .join(
            Skill,
            JobSkill.skill_id == Skill.skill_id
        )
        .filter(
            JobSkill.job_id == job_id
        )
        .all()
    )

    criteria = (
        db.query(EvaluationCriteria)
        .filter(
            EvaluationCriteria.job_id == job_id
        )
        .all()
    )

    return {
        "job_id": job.job_id,
        "job_title": job.job_title,
        "job_description": job.job_description,
        "minimum_experience": job.minimum_experience,

        "skills": [
            {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "skill_type": job_skill.skill_type
            }
            for job_skill, skill in skills
        ],

        "evaluation_criteria": [
            {
                "criteria_id": criterion.criteria_id,
                "criteria_name": criterion.criteria_name,
                "criteria_type": criterion.criteria_type,
                "criteria_description": criterion.criteria_description,
                "weight": criterion.weight,
                "max_score": criterion.max_score
            }
            for criterion in criteria
        ]
    }








@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }










@router.get("/{job_id}/skills")
def get_job_skills(
    job_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    job = (
        db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    skills = (
        db.query(JobSkill, Skill)
        .join(
            Skill,
            JobSkill.skill_id == Skill.skill_id
        )
        .filter(
            JobSkill.job_id == job_id
        )
        .all()
    )

    return [
        {
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "skill_category": skill.skill_category,
            "skill_type": job_skill.skill_type
        }
        for job_skill, skill in skills
    ]







@router.delete("/{job_id}/skills/{skill_id}")
def delete_job_skill(
    job_id: int,
    skill_id: int,
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

    job_skill = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id
        )
        .first()
    )

    if not job_skill:
        raise HTTPException(
            status_code=404,
            detail="Skill is not associated with this job"
        )

    db.delete(job_skill)
    db.commit()

    return {
        "message": "Skill removed from job",
        "job_id": job_id,
        "skill_id": skill_id
    }










