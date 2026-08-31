from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.candidate import Candidate
from models.user import User
from models.skill import CandidateSkill,Skill
from models.project import Project
from schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate
)
from models.experience import Experience
from models.qualification import Qualification
from utils.auth import get_current_user
from schemas.experience import ExperienceCreate
from schemas.project import ProjectCreate,ProjectResponse
from schemas.qualification import QualificationCreate
from schemas.skill import CandidateSkillCreate


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



@router.post("/{candidate_id}/skills")
def add_candidate_skill(
    candidate_id: int,
    skill_data: CandidateSkillCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    # Check candidate belongs to current user
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

    # Check skill exists
    skill = (
        db.query(Skill)
        .filter(
            Skill.skill_id == skill_data.skill_id
        )
        .first()
    )

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    # Prevent duplicate skill
    existing_skill = (
        db.query(CandidateSkill)
        .filter(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_data.skill_id
        )
        .first()
    )

    if existing_skill:
        raise HTTPException(
            status_code=400,
            detail="Candidate already has this skill"
        )

    # Create candidate skill
    candidate_skill = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_data.skill_id,
        proficiency=skill_data.proficiency,
        years_experience=skill_data.years_experience
    )

    db.add(candidate_skill)
    db.commit()
    db.refresh(candidate_skill)

    return {
        "message": "Skill added successfully",
        "candidate_id": candidate_id,
        "skill_id": skill.skill_id,
        "skill_name": skill.skill_name,
        "skill_category": skill.skill_category,
        "proficiency": candidate_skill.proficiency,
        "years_experience": candidate_skill.years_experience
    }








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





@router.post("/{candidate_id}/qualifications")
def add_qualification(
    candidate_id: int,
    qualification_data: QualificationCreate,
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

    qualification = Qualification(
        candidate_id=candidate_id,
        university=qualification_data.university,
        degree=qualification_data.degree,
        specialization=qualification_data.specialization,
        percentage=qualification_data.percentage,
        passed_out_year=qualification_data.passed_out_year,
        joining_year=qualification_data.joining_year
    )

    db.add(qualification)
    db.commit()
    db.refresh(qualification)

    return qualification


















@router.post("/{candidate_id}/experience")
def add_experience(
    candidate_id: int,
    experience_data: ExperienceCreate,
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

    experience = Experience(
        candidate_id=candidate_id,
        company_name=experience_data.company_name,
        job_title=experience_data.job_title,
        start_date=experience_data.start_date,
        end_date=experience_data.end_date,
        years=experience_data.years,
        description=experience_data.description
    )

    db.add(experience)
    db.commit()
    db.refresh(experience)

    return experience








@router.post("/{candidate_id}/projects")
def add_project(
    candidate_id: int,
    project_data: ProjectCreate,
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

    project = Project(
        candidate_id=candidate_id,
        project_name=project_data.project_name,
        description=project_data.description,
        technologies=project_data.technologies,
        role=project_data.role,
        duration=project_data.duration
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project



@router.get(
    "/{id}/projects",
    response_model=list[ProjectResponse]
)
def get_candidate_projects(
    id: int,
    db: Session = Depends(getdb)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.candidate_id == id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate.projects