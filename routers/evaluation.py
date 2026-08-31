from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import getdb
from models.job import Job
from models.evaluation import EvaluationCriteria
from models.user import User
from schemas.evaluation import EvaluationCriteriaCreate
from utils.auth import get_current_user
from models.evaluation_run import EvaluationRun
from models.evaluation_result import EvaluationResult
from models.ranking import CandidateRanking
from models.candidate import Candidate
from datetime import datetime,  timezone
from schemas.evaluation import (
    EvaluationCriteriaCreate,
    EvaluationCriteriaUpdate
)
from services.ranking_service import calculate_candidate_scores


router = APIRouter(
    prefix="/job",
    tags=["Evaluation"]
)


@router.post("/{job_id}/criteria")
def create_evaluation_criteria(job_id: int,criteria_data: EvaluationCriteriaCreate,db: Session = Depends(getdb),current_user: User = Depends(get_current_user)):


    job = (db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first())

    if not job:
        raise HTTPException(status_code=404,detail="Job not found")

  

    current_total = (db.query(EvaluationCriteria).filter(EvaluationCriteria.job_id == job_id).with_entities(EvaluationCriteria.weight).all()
    )

    current_weight = sum(weight[0] for weight in current_total)

  

    if current_weight + criteria_data.weight > 100:
        raise HTTPException(status_code=400,detail=f"Total weight cannot exceed 100. Current weight: {current_weight}")

   

    existing = (db.query(EvaluationCriteria).filter(EvaluationCriteria.job_id == job_id,EvaluationCriteria.criteria_name == criteria_data.criteria_name).first())

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




@router.get("/{job_id}/criteria")
def get_criteria(
    job_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    job = (db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first())

    if not job:
        raise HTTPException(status_code=404,detail="Job not found")

    criteria = (db.query(EvaluationCriteria).filter(EvaluationCriteria.job_id == job_id).all())

    total_weight = sum(
        criterion.weight
        for criterion in criteria
    )

    return {
        "job_id": job_id,
        "total_weight": total_weight,
        "criteria": criteria
    }






@router.put("/{job_id}/criteria/{criteria_id}")
def update_criteria(
    job_id: int,
    criteria_id: int,
    criteria_data: EvaluationCriteriaUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    job = (db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first())

    if not job:
        raise HTTPException(status_code=404,detail="Job not found")

    criterion = (db.query(EvaluationCriteria).filter(EvaluationCriteria.criteria_id == criteria_id,EvaluationCriteria.job_id == job_id).first())

    if not criterion:
        raise HTTPException(
            status_code=404,
            detail="Evaluation criterion not found"
        )

    new_weight = (
        criteria_data.weight
        if criteria_data.weight is not None
        else criterion.weight
    )

    other_criteria = (
        db.query(EvaluationCriteria)
        .filter(
            EvaluationCriteria.job_id == job_id,
            EvaluationCriteria.criteria_id != criteria_id
        )
        .all()
    )

    other_weight = sum(
        item.weight
        for item in other_criteria
    )

    if other_weight + new_weight > 100:
        raise HTTPException(
            status_code=400,
            detail="Total weight cannot exceed 100"
        )

    if criteria_data.criteria_name is not None:
        criterion.criteria_name = criteria_data.criteria_name

    if criteria_data.criteria_type is not None:
        criterion.criteria_type = criteria_data.criteria_type

    if criteria_data.criteria_description is not None:
        criterion.criteria_description = (
            criteria_data.criteria_description
        )

    if criteria_data.weight is not None:
        criterion.weight = criteria_data.weight

    if criteria_data.max_score is not None:
        criterion.max_score = criteria_data.max_score

    db.commit()
    db.refresh(criterion)

    return {
        "message": "Evaluation criterion updated successfully",
        "criteria_id": criterion.criteria_id,
        "criteria_name": criterion.criteria_name,
        "criteria_type": criterion.criteria_type,
        "weight": criterion.weight,
        "max_score": criterion.max_score
    }






@router.delete("/{job_id}/criteria/{criteria_id}")
def delete_criteria(
    job_id: int,
    criteria_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    job = (
        db.query(Job).filter(Job.job_id == job_id,Job.user_id == current_user.user_id).first()
    )

    if not job:
        raise HTTPException(status_code=404,detail="Job not found")

    criterion = (db.query(EvaluationCriteria).filter(EvaluationCriteria.criteria_id == criteria_id,EvaluationCriteria.job_id == job_id).first())

    if not criterion:
        raise HTTPException(status_code=404,detail="Evaluation criterion not found")

    db.delete(criterion)
    db.commit()

    return {
        "message": "Evaluation criterion deleted successfully",
        "criteria_id": criteria_id
    }
























@router.post("/{job_id}/rank")
def rank_candidates(
    job_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    # 1. Get job
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

    # 2. Get criteria
    criteria = (
        db.query(EvaluationCriteria)
        .filter(
            EvaluationCriteria.job_id == job_id
        )
        .all()
    )

    if not criteria:
        raise HTTPException(
            status_code=400,
            detail="No evaluation criteria found"
        )

    # 3. Check total weight
    total_weight = sum(
        criterion.weight
        for criterion in criteria
    )

    if total_weight != 100:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Evaluation criteria weights must total 100. "
                f"Current total: {total_weight}"
            )
        )

    # 4. Get candidates
    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.user_id == current_user.user_id
        )
        .all()
    )

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No candidates found"
        )

    # 5. CREATE EVALUATION RUN
    evaluation_run = EvaluationRun(
        job_id=job_id,
        run_name=(
            "Ranking Run - "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        total_candidates=len(candidates)
    )

    db.add(evaluation_run)

    # Important:
    # Generates evaluation_run_id before we create results
    db.flush()

    try:

        # This will temporarily hold
        # candidate_id + final_score
        candidate_scores = []

        # =================================================
        # 6. EVALUATE EACH CANDIDATE
        # =================================================

        for candidate in candidates:

            final_score, results = calculate_candidate_scores(
                candidate=candidate,
                job=job,
                criteria=criteria,
                db=db
            )

            # =============================================
            # 7. SAVE EACH CRITERION RESULT
            # =============================================

            for result_data in results:

                evaluation_result = EvaluationResult(
                    evaluation_run_id=(
                        evaluation_run.evaluation_run_id
                    ),
                    candidate_id=candidate.candidate_id,
                    criteria_id=result_data["criteria_id"],
                    score=result_data["score"],
                    reason=result_data["reason"]
                )

                db.add(evaluation_result)

            # =============================================
            # 8. STORE FINAL SCORE TEMPORARILY
            # =============================================

            candidate_scores.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "final_score": final_score
                }
            )

        # =================================================
        # 9. SORT CANDIDATES
        # =================================================

        candidate_scores.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        # =================================================
        # 10. CREATE FINAL RANKINGS
        # =================================================

        for position, data in enumerate(
            candidate_scores,
            start=1
        ):

            final_score = data["final_score"]

            if final_score >= 80:
                recommendation = "Strong Match"

            elif final_score >= 60:
                recommendation = "Good Match"

            elif final_score >= 40:
                recommendation = "Potential Match"

            else:
                recommendation = "Not Recommended"

            ranking = CandidateRanking(
                evaluation_run_id=(
                    evaluation_run.evaluation_run_id
                ),
                candidate_id=data["candidate_id"],
                final_score=final_score,
                rank_position=position,
                recommendation=recommendation
            )

            db.add(ranking)

        # =================================================
        # 11. SAVE EVERYTHING
        # =================================================

        db.commit()

        db.refresh(evaluation_run)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Ranking failed: {str(e)}"
        )

    # =====================================================
    # 12. RESPONSE
    # =====================================================

    return {
        "message": "Candidate ranking completed successfully",
        "evaluation_run_id": evaluation_run.evaluation_run_id,
        "job_id": job_id,
        "run_name": evaluation_run.run_name,
        "total_candidates": evaluation_run.total_candidates
    }





@router.get("/{job_id}/evaluation-runs")
def get_evaluation_runs(
    job_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    # Check job belongs to current user
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

    runs = (
        db.query(EvaluationRun)
        .filter(
            EvaluationRun.job_id == job_id
        )
        .order_by(
            EvaluationRun.created_at.desc()
        )
        .all()
    )

    return {
        "job_id": job_id,
        "evaluation_runs": [
            {
                "evaluation_run_id": run.evaluation_run_id,
                "job_id": run.job_id,
                "run_name": run.run_name,
                "total_candidates": run.total_candidates,
                "created_at": run.created_at
            }
            for run in runs
        ]
    }







@router.get("/evaluation-runs/{run_id}")
def get_evaluation_run(
    run_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    run = (
        db.query(EvaluationRun)
        .join(Job)
        .filter(
            EvaluationRun.evaluation_run_id == run_id,
            Job.user_id == current_user.user_id
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    return {
        "evaluation_run_id": run.evaluation_run_id,
        "job_id": run.job_id,
        "run_name": run.run_name,
        "total_candidates": run.total_candidates,
        "created_at": run.created_at
    }


@router.get("/evaluation-runs/{run_id}/rankings")
def get_rankings(
    run_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

  
    run = (
        db.query(EvaluationRun)
        .join(Job)
        .filter(
            EvaluationRun.evaluation_run_id == run_id,
            Job.user_id == current_user.user_id
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    rankings = (
        db.query(CandidateRanking)
        .filter(
            CandidateRanking.evaluation_run_id == run_id
        )
        .order_by(
            CandidateRanking.final_score.desc()
        )
        .all()
    )

    return {
        "evaluation_run_id": run_id,
        "rankings": [
            {
                "ranking_id": ranking.ranking_id,
                "candidate_id": ranking.candidate_id,
                "final_score": ranking.final_score,
                "rank_position": ranking.rank_position,
                "recommendation": ranking.recommendation,
                "created_at": ranking.created_at,
                "updated_at": ranking.updated_at
            }
            for ranking in rankings
        ]
    }













@router.get(
    "/evaluation-runs/{run_id}/candidates/{candidate_id}"
)
def get_candidate_evaluation(
    run_id: int,
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

   

    run = (
        db.query(EvaluationRun)
        .join(Job)
        .filter(
            EvaluationRun.evaluation_run_id == run_id,
            Job.user_id == current_user.user_id
        )
        .first()
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found"
        )

    

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_id == candidate_id,
            Candidate.user_id == current_user.user_id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )


    ranking = (
        db.query(CandidateRanking)
        .filter(
            CandidateRanking.evaluation_run_id == run_id,
            CandidateRanking.candidate_id == candidate_id
        )
        .first()
    )

    if not ranking:
        raise HTTPException(
            status_code=404,
            detail="Candidate ranking not found"
        )

   

    results = (
        db.query(EvaluationResult)
        .filter(
            EvaluationResult.evaluation_run_id == run_id,
            EvaluationResult.candidate_id == candidate_id
        )
        .all()
    )

    return {
        "evaluation_run_id": run_id,
        "candidate_id": candidate_id,

        "ranking": {
            "ranking_id": ranking.ranking_id,
            "final_score": ranking.final_score,
            "rank_position": ranking.rank_position,
            "recommendation": ranking.recommendation
        },

        "criteria_results": [
            {
                "result_id": result.result_id,
                "criteria_id": result.criteria_id,
                "score": result.score,
                "reason": result.reason,
                "created_at": result.created_at
            }
            for result in results
        ]
    }



