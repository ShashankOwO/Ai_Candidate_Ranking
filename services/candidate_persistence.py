import re
from datetime import datetime, date
from sqlalchemy.orm import Session

from models.candidate import Candidate
from models.skill import Skill, CandidateSkill
from models.experience import Experience
from models.qualification import Qualification
from models.project import Project
from schemas.candidate_extraction import CandidateExtraction


def _parse_date(val: str | None) -> date | None:
    if not val or not isinstance(val, str):
        return None
    val = val.strip()
    # Try YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%b %Y", "%B %Y", "%Y"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    # Extract 4 digit year as fallback (e.g. "2021")
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


def save_candidate_data(extracted_data: CandidateExtraction, user_id: int, db: Session):
    candidate = Candidate(
        user_id=user_id,
        full_name=extracted_data.full_name,
        contact_no=extracted_data.contact_no,
        email_address=extracted_data.email_address
    )

    db.add(candidate)
    db.flush()

    for extracted_skill in extracted_data.skills:
        skill = db.query(Skill).filter(Skill.skill_name.ilike(extracted_skill.skill_name.strip())).first()

        if not skill:
            skill = Skill(
                skill_name=extracted_skill.skill_name.strip(),
                skill_category=extracted_skill.skill_category or "Technical"
            )
            db.add(skill)
            db.flush()

        candidate_skill = CandidateSkill(
            candidate_id=candidate.candidate_id,
            skill_id=skill.skill_id,
            proficiency=extracted_skill.proficiency,
            years_experience=_parse_int(extracted_skill.years_experience)
        )
        db.add(candidate_skill)

    for extracted_experience in extracted_data.experiences:
        experience = Experience(
            candidate_id=candidate.candidate_id,
            company_name=extracted_experience.company_name,
            job_title=extracted_experience.job_title,
            start_date=_parse_date(extracted_experience.start_date),
            end_date=_parse_date(extracted_experience.end_date),
            years=_parse_int(extracted_experience.years),
            description=extracted_experience.description
        )
        db.add(experience)

    for extracted_qualification in extracted_data.qualifications:
        qualification = Qualification(
            candidate_id=candidate.candidate_id,
            university=extracted_qualification.university,
            degree=extracted_qualification.degree,
            specialization=extracted_qualification.specialization,
            percentage=extracted_qualification.percentage,
            passed_out_year=_parse_int(extracted_qualification.passed_out_year),
            joining_year=_parse_int(extracted_qualification.joining_year)
        )
        db.add(qualification)

    for extracted_project in extracted_data.projects:
        project = Project(
            candidate_id=candidate.candidate_id,
            project_name=extracted_project.project_name,
            description=extracted_project.description,
            technologies=extracted_project.technologies,
            role=extracted_project.role,
            duration=extracted_project.duration
        )
        db.add(project)

    db.commit()
    db.refresh(candidate)

    return candidate
