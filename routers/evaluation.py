from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.job import Job
from models.evaluation import EvaluationCriteria
from models.user import User
from schemas.evaluation import EvaluationCriteriaCreate
from utils.auth import get_current_user


router = APIRouter(
    prefix="/jobs",
    tags=["Evaluation Criteria"]
)


@router.post("/{job_id}/criteria")
def create_evaluation_criteria(
    job_id: int,
    criteria_data: EvaluationCriteriaCreate,
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

  

    current_total = (
        db.query(EvaluationCriteria)
        .filter(
            EvaluationCriteria.job_id == job_id
        )
        .with_entities(
            EvaluationCriteria.weight
        )
        .all()
    )

    current_weight = sum(
        weight[0]
        for weight in current_total
    )

  

    if current_weight + criteria_data.weight > 100:
        raise HTTPException(
            status_code=400,
            detail=f"Total weight cannot exceed 100. Current weight: {current_weight}"
        )

   

    existing = (
        db.query(EvaluationCriteria)
        .filter(
            EvaluationCriteria.job_id == job_id,
            EvaluationCriteria.criteria_name == criteria_data.criteria_name
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This evaluation criterion already exists for this job"
        )

  

    criterion = EvaluationCriteria(
        job_id=job_id,
        criteria_name=criteria_data.criteria_name,
        criteria_type=criteria_data.criteria_type,
        criteria_description=criteria_data.criteria_description,
        weight=criteria_data.weight,
        max_score=criteria_data.max_score
    )

    db.add(criterion)
    db.commit()
    db.refresh(criterion)

    return {
        "message": "Evaluation criterion created successfully",
        "criteria_id": criterion.criteria_id,
        "job_id": criterion.job_id,
        "criteria_name": criterion.criteria_name,
        "criteria_type": criterion.criteria_type,
        "weight": criterion.weight
    }