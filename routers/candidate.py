import re
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import getdb
from models.candidate import Candidate
from models.user import User
from models.skill import CandidateSkill, Skill
from models.project import Project
from models.experience import Experience
from models.qualification import Qualification
from utils.auth import get_current_user

from schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate
)
from schemas.experience import (
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse
)
from schemas.qualification import (
    QualificationCreate,
    QualificationUpdate,
    QualificationResponse
)
from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)
from schemas.skill import (
    CandidateSkillCreate,
    CandidateSkillUpdate
)


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


def _parse_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    if not isinstance(val, str):
        return None
    val = val.strip()
    if not val:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%b %Y", "%B %Y", "%Y"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', val)
    if year_match:
        try:
            return date(int(year_match.group(1)), 1, 1)
        except ValueError:
            pass
    return None


def _parse_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(round(float(str(val).strip())))
    except (ValueError, TypeError):
        return None


def _get_user_candidate(candidate_id: int, db: Session, user_id: int) -> Candidate:
    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_id == candidate_id,
            Candidate.user_id == user_id
        )
        .first()
    )
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )
    return candidate


# ============================================================================
# CANDIDATE CORE CRUD
# ============================================================================

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
        .order_by(Candidate.created_at.desc())
        .all()
    )
    return candidates


@router.get(
    "/{id}",
    response_model=CandidateResponse
)
def get_candidate_by_id(
    id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    return _get_user_candidate(id, db, current_user.user_id)


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
    candidate = _get_user_candidate(id, db, current_user.user_id)

    update_data = candidate_data.model_dump(exclude_unset=True)
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
    candidate = _get_user_candidate(id, db, current_user.user_id)

    db.delete(candidate)
    db.commit()

    return {
        "message": "Candidate deleted successfully",
        "candidate_id": id
    }


# ============================================================================
# CANDIDATE SKILLS CRUD
# ============================================================================

@router.get("/{candidate_id}/skills")
def get_candidate_skills(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

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
    _get_user_candidate(candidate_id, db, current_user.user_id)

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

    existing_skill = (
        db.query(CandidateSkill)
        .filter(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_data.skill_id
        )
        .first()
    )

    if existing_skill:
        # If already exists, update proficiency and years
        if skill_data.proficiency is not None:
            existing_skill.proficiency = skill_data.proficiency
        if skill_data.years_experience is not None:
            existing_skill.years_experience = _parse_int(skill_data.years_experience)
        db.commit()
        db.refresh(existing_skill)
        return {
            "message": "Skill updated successfully",
            "candidate_id": candidate_id,
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "skill_category": skill.skill_category,
            "proficiency": existing_skill.proficiency,
            "years_experience": existing_skill.years_experience
        }

    candidate_skill = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_data.skill_id,
        proficiency=skill_data.proficiency,
        years_experience=_parse_int(skill_data.years_experience)
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


@router.put("/{candidate_id}/skills/{skill_id}")
def update_candidate_skill(
    candidate_id: int,
    skill_id: int,
    skill_data: CandidateSkillUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    candidate_skill = (
        db.query(CandidateSkill)
        .filter(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_id
        )
        .first()
    )

    if not candidate_skill:
        raise HTTPException(
            status_code=404,
            detail="Candidate skill not found"
        )

    if skill_data.proficiency is not None:
        candidate_skill.proficiency = skill_data.proficiency
    if skill_data.years_experience is not None:
        candidate_skill.years_experience = _parse_int(skill_data.years_experience)

    db.commit()
    db.refresh(candidate_skill)

    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()

    return {
        "message": "Skill updated successfully",
        "candidate_id": candidate_id,
        "skill_id": skill_id,
        "skill_name": skill.skill_name if skill else "",
        "proficiency": candidate_skill.proficiency,
        "years_experience": candidate_skill.years_experience
    }


@router.delete("/{candidate_id}/skills/{skill_id}")
def delete_candidate_skill(
    candidate_id: int,
    skill_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    candidate_skill = (
        db.query(CandidateSkill)
        .filter(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_id
        )
        .first()
    )

    if not candidate_skill:
        raise HTTPException(
            status_code=404,
            detail="Candidate skill not found"
        )

    db.delete(candidate_skill)
    db.commit()

    return {
        "message": "Skill removed from candidate successfully",
        "candidate_id": candidate_id,
        "skill_id": skill_id
    }


# ============================================================================
# CANDIDATE EXPERIENCE CRUD
# ============================================================================

@router.get(
    "/{candidate_id}/experience",
    response_model=list[ExperienceResponse]
)
def get_candidate_experience(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    experiences = (
        db.query(Experience)
        .filter(
            Experience.candidate_id == candidate_id
        )
        .order_by(Experience.experience_id.asc())
        .all()
    )

    return experiences


@router.post(
    "/{candidate_id}/experience",
    response_model=ExperienceResponse
)
def add_experience(
    candidate_id: int,
    experience_data: ExperienceCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    experience = Experience(
        candidate_id=candidate_id,
        company_name=experience_data.company_name,
        job_title=experience_data.job_title,
        start_date=_parse_date(experience_data.start_date),
        end_date=_parse_date(experience_data.end_date),
        years=_parse_int(experience_data.years),
        description=experience_data.description
    )

    db.add(experience)
    db.commit()
    db.refresh(experience)

    return experience


@router.put(
    "/{candidate_id}/experience/{experience_id}",
    response_model=ExperienceResponse
)
def update_experience(
    candidate_id: int,
    experience_id: int,
    experience_data: ExperienceUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    experience = (
        db.query(Experience)
        .filter(
            Experience.experience_id == experience_id,
            Experience.candidate_id == candidate_id
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience record not found"
        )

    if experience_data.company_name is not None:
        experience.company_name = experience_data.company_name
    if experience_data.job_title is not None:
        experience.job_title = experience_data.job_title
    if experience_data.start_date is not None:
        experience.start_date = _parse_date(experience_data.start_date)
    if experience_data.end_date is not None:
        experience.end_date = _parse_date(experience_data.end_date)
    if experience_data.years is not None:
        experience.years = _parse_int(experience_data.years)
    if experience_data.description is not None:
        experience.description = experience_data.description

    db.commit()
    db.refresh(experience)

    return experience


@router.delete("/{candidate_id}/experience/{experience_id}")
def delete_experience(
    candidate_id: int,
    experience_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    experience = (
        db.query(Experience)
        .filter(
            Experience.experience_id == experience_id,
            Experience.candidate_id == candidate_id
        )
        .first()
    )

    if not experience:
        raise HTTPException(
            status_code=404,
            detail="Experience record not found"
        )

    db.delete(experience)
    db.commit()

    return {
        "message": "Experience deleted successfully",
        "experience_id": experience_id,
        "candidate_id": candidate_id
    }


# ============================================================================
# CANDIDATE QUALIFICATIONS (EDUCATION) CRUD
# ============================================================================

@router.get(
    "/{candidate_id}/qualifications",
    response_model=list[QualificationResponse]
)
def get_candidate_qualifications(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    qualifications = (
        db.query(Qualification)
        .filter(
            Qualification.candidate_id == candidate_id
        )
        .order_by(Qualification.qualification_id.asc())
        .all()
    )

    return qualifications


@router.post(
    "/{candidate_id}/qualifications",
    response_model=QualificationResponse
)
def add_qualification(
    candidate_id: int,
    qualification_data: QualificationCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    qualification = Qualification(
        candidate_id=candidate_id,
        university=qualification_data.university,
        degree=qualification_data.degree,
        specialization=qualification_data.specialization,
        percentage=qualification_data.percentage,
        passed_out_year=_parse_int(qualification_data.passed_out_year),
        joining_year=_parse_int(qualification_data.joining_year)
    )

    db.add(qualification)
    db.commit()
    db.refresh(qualification)

    return qualification


@router.put(
    "/{candidate_id}/qualifications/{qualification_id}",
    response_model=QualificationResponse
)
def update_qualification(
    candidate_id: int,
    qualification_id: int,
    qualification_data: QualificationUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    qualification = (
        db.query(Qualification)
        .filter(
            Qualification.qualification_id == qualification_id,
            Qualification.candidate_id == candidate_id
        )
        .first()
    )

    if not qualification:
        raise HTTPException(
            status_code=404,
            detail="Qualification record not found"
        )

    if qualification_data.university is not None:
        qualification.university = qualification_data.university
    if qualification_data.degree is not None:
        qualification.degree = qualification_data.degree
    if qualification_data.specialization is not None:
        qualification.specialization = qualification_data.specialization
    if qualification_data.percentage is not None:
        qualification.percentage = qualification_data.percentage
    if qualification_data.passed_out_year is not None:
        qualification.passed_out_year = _parse_int(qualification_data.passed_out_year)
    if qualification_data.joining_year is not None:
        qualification.joining_year = _parse_int(qualification_data.joining_year)

    db.commit()
    db.refresh(qualification)

    return qualification


@router.delete("/{candidate_id}/qualifications/{qualification_id}")
def delete_qualification(
    candidate_id: int,
    qualification_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    qualification = (
        db.query(Qualification)
        .filter(
            Qualification.qualification_id == qualification_id,
            Qualification.candidate_id == candidate_id
        )
        .first()
    )

    if not qualification:
        raise HTTPException(
            status_code=404,
            detail="Qualification record not found"
        )

    db.delete(qualification)
    db.commit()

    return {
        "message": "Qualification deleted successfully",
        "qualification_id": qualification_id,
        "candidate_id": candidate_id
    }


# ============================================================================
# CANDIDATE PROJECTS CRUD
# ============================================================================

@router.get(
    "/{candidate_id}/projects",
    response_model=list[ProjectResponse]
)
def get_candidate_projects(
    candidate_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    projects = (
        db.query(Project)
        .filter(
            Project.candidate_id == candidate_id
        )
        .order_by(Project.project_id.asc())
        .all()
    )

    return projects


@router.post(
    "/{candidate_id}/projects",
    response_model=ProjectResponse
)
def add_project(
    candidate_id: int,
    project_data: ProjectCreate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

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


@router.put(
    "/{candidate_id}/projects/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    candidate_id: int,
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    project = (
        db.query(Project)
        .filter(
            Project.project_id == project_id,
            Project.candidate_id == candidate_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project record not found"
        )

    if project_data.project_name is not None:
        project.project_name = project_data.project_name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.technologies is not None:
        project.technologies = project_data.technologies
    if project_data.role is not None:
        project.role = project_data.role
    if project_data.duration is not None:
        project.duration = project_data.duration

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{candidate_id}/projects/{project_id}")
def delete_project(
    candidate_id: int,
    project_id: int,
    db: Session = Depends(getdb),
    current_user: User = Depends(get_current_user)
):
    _get_user_candidate(candidate_id, db, current_user.user_id)

    project = (
        db.query(Project)
        .filter(
            Project.project_id == project_id,
            Project.candidate_id == candidate_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project record not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully",
        "project_id": project_id,
        "candidate_id": candidate_id
    }