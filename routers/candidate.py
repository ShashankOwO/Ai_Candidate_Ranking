from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
 
from database import getdb
from models.candidate import Candidate
from models.user import User
from schemas.candidate import (
    CandidateCreate,
    CandidateResponse
)
from utils.auth import get_current_user
 
 
router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)
 
 
@router.post(
    "/",
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
    "/",
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