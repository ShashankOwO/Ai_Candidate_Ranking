from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.candidate import Candidate
from models.user import User
from models.skill import CandidateSkill,Skill
from schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate
)
from models.experience import Experience
from models.qualification import Qualification
from utils.auth import get_current_user


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)
 
@router.post(
    "/create",
    response_model=CandidateResponse
)
def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    candidate = Candidate(
        user_id=current_user.user_id,
        full_name=candidate_data.full_name,
        contact_no=candidate_data.contact_no,
        email_address=candidate_data.email_address
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


@router.get(
    "/all",
    response_model=list[CandidateResponse]
)
def get_candidates(
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.user_id == current_user.user_id
        )
        .all()
    )

    return candidates


@router.put(
    "/{id}",
    response_model=CandidateResponse
)
def update_candidate(
    id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_id == id,
            Candidate.user_id == current_user.user_id
        )
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    update_data = candidate_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)

    return candidate


@router.delete(
    "/{id}"
)
def delete_candidate(
    id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_id == id,
            Candidate.user_id == current_user.user_id
        )
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)
    db.commit()

    return {
        "message": "Candidate deleted successfully",
        "candidate_id": id
    }










@router.get("/{candidate_id}/skills")
def get_candidate_skills(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

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

    skills = (
        db.query(CandidateSkill, Skill)
        .join(
            Skill,
            CandidateSkill.skill_id == Skill.skill_id
        )
        .filter(
            CandidateSkill.candidate_id == candidate_id
        )
        .all()
    )

    return [
        {
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "skill_category": skill.skill_category,
            "proficiency": candidate_skill.proficiency,
            "years_experience": candidate_skill.years_experience
        }
        for candidate_skill, skill in skills
    ]









@router.get("/{candidate_id}/experience")
def get_candidate_experience(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

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

    experiences = (
        db.query(Experience)
        .filter(
            Experience.candidate_id == candidate_id
        )
        .all()
    )

    return experiences




@router.get("/{candidate_id}/qualifications")
def get_candidate_qualifications(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):

    candidate = (
        db.query(Candidate).filter(Candidate.candidate_id == candidate_id,Candidate.user_id == current_user.user_id).first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    qualifications = (
        db.query(Qualification)
        .filter(
            Qualification.candidate_id == candidate_id
        )
        .all()
    )

    return qualifications