from sqlalchemy.orm import Session

from models.candidate import Candidate
from models.skill import Skill,CandidateSkill
from models.job import JobSkill,Job
from models.experience import Experience
from models.qualification import Qualification
from models.project import Project
from models.evaluation import EvaluationCriteria
from services.ai_evaluator import evaluate_ai_criteria


def calculate_skill_score(
    candidate_id: int,
    job_id: int,
    db: Session
):

    job_skills = (
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

    if not job_skills:
        return 0, "No skills configured for this job."

    candidate_skills = (
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

    candidate_skill_map = {
        skill.skill_name.lower(): candidate_skill
        for candidate_skill, skill in candidate_skills
    }

    total_weight = 0
    matched_weight = 0

    matched_skills = []
    missing_skills = []

    for job_skill, skill in job_skills:

        if job_skill.skill_type.lower() == "required":
            skill_weight = 2
        else:
            skill_weight = 1

        total_weight += skill_weight

        if skill.skill_name.lower() in candidate_skill_map:

            matched_weight += skill_weight

            matched_skills.append(
                skill.skill_name
            )

        else:

            missing_skills.append(
                skill.skill_name
            )

    if total_weight == 0:
        return 0, "No valid job skills."

    score = (
        matched_weight / total_weight
    ) * 100

    reason = (
        f"Matched skills: "
        f"{', '.join(matched_skills) or 'None'}. "
        f"Missing skills: "
        f"{', '.join(missing_skills) or 'None'}."
    )

    return round(score, 2), reason




def calculate_experience_score(
    candidate_id: int,
    job: Job,
    db: Session
):

    experiences = (
        db.query(Experience)
        .filter(
            Experience.candidate_id == candidate_id
        )
        .all()
    )

    if not experiences:
        return 0, "No professional experience found."

    total_years = sum(
        experience.years or 0
        for experience in experiences
    )

    required_years = (
        job.minimum_experience or 0
    )

    if required_years == 0:

        return (
            100,
            "No minimum experience requirement."
        )

    score = (
        total_years / required_years
    ) * 100

    score = min(score, 100)

    reason = (
        f"Candidate has {total_years} years "
        f"of experience. "
        f"Job requires {required_years} years."
    )

    return round(score, 2), reason





def calculate_qualification_score(candidate_id:int,db:Session)->tuple[float,str]:

    qualifications=db.query(Qualification).filter(Qualification.candidate_id==candidate_id).all()

    if not qualifications:
        return 0,"No qualification information found."

    score=0

    for qualification in qualifications:

        if qualification.degree:
            score+=50
        if qualification.specialization:
            score+=50
        if qualification.university:
            score+=20

        break

    reason="Qualification information found."

    return min(score,100),reason


def calculate_project_score(candidate_id:int,db:Session)->tuple[float,str]:

    projects=db.query(Project).filter(Project.candidate_id==candidate_id).all()

    if not projects:
        return 0,"No Projects found."

    project_count=len(projects)
    score=0

    if project_count>=3:
        score=100
    elif project_count==2:
        score=80
    else:
        score=60

    reason=(f"Candidate has {project_count} project(s)")

    return score,reason
















def build_candidate_information(
    candidate_id: int,
    db: Session
):

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_id == candidate_id
        )
        .first()
    )

    if not candidate:
        return ""

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

    experiences = (
        db.query(Experience)
        .filter(
            Experience.candidate_id == candidate_id
        )
        .all()
    )

    qualifications = (
        db.query(Qualification)
        .filter(
            Qualification.candidate_id == candidate_id
        )
        .all()
    )

    projects = (
        db.query(Project)
        .filter(
            Project.candidate_id == candidate_id
        )
        .all()
    )

    information = f"""
Candidate Name:
{candidate.full_name}

Email:
{candidate.email_address}

Skills:
"""

    for candidate_skill, skill in skills:

        information += f"""
- Skill: {skill.skill_name}
- Category: {skill.skill_category}
- Proficiency: {candidate_skill.proficiency}
- Years Experience: {candidate_skill.years_experience}
"""

    information += """

Experience:
"""

    for experience in experiences:

        information += f"""
- Company: {experience.company_name}
- Job Title: {experience.job_title}
- Years: {experience.years}
- Description: {experience.description}
"""

    information += """

Qualifications:
"""

    for qualification in qualifications:

        information += f"""
- University: {qualification.university}
- Degree: {qualification.degree}
- Specialization: {qualification.specialization}
- Percentage: {qualification.percentage}
- Passed Out Year: {qualification.passed_out_year}
"""

    information += """

Projects:
"""

    for project in projects:

        information += f"""
- Project Name: {project.project_name}
- Description: {project.description}
- Technologies: {project.technologies}
- Role: {project.role}
- Duration: {project.duration}
"""

    return information




def parse_ai_result(
    ai_result: str
) -> tuple[float, str]:

    lines = ai_result.splitlines()

    score = 0
    reason = "No reason provided."

    for line in lines:

        if line.lower().startswith("score:"):

            score_text = line.split(
                ":", 
                1
            )[1].strip()

            try:
                score = float(score_text)

            except ValueError:
                score = 0

        elif line.lower().startswith("reason:"):

            reason = line.split(
                ":",
                1
            )[1].strip()

    score = max(
        0,
        min(score, 100)
    )

    return round(score, 2), reason





def is_ai_criterion(criterion):

    return criterion.criteria_type in [
        "qualification",
        "projects",
        "custom"
    ]




def calculate_candidate_scores(
    candidate: Candidate,
    job: Job,
    criteria: list[EvaluationCriteria],
    db: Session
):

    final_score = 0

    results = []

    ai_criteria = [
        criterion
        for criterion in criteria
        if criterion.criteria_type.lower()
        in [
            "qualification",
            "projects",
            "custom"
        ]
    ]

    ai_results = {}

    if ai_criteria:

        candidate_information = (
            build_candidate_information(
                candidate.candidate_id,
                db
            )
        )

        ai_output = evaluate_ai_criteria(
            job_description=job.job_description,
            candidate_information=candidate_information,
            criteria=ai_criteria
        )

        for item in ai_output:

            ai_results[
                item["criteria_id"]
            ] = item

    for criterion in criteria:

        score = 0
        reason = ""

        criterion_type = (
            criterion.criteria_type.lower()
        )

        if criterion_type == "skills":

            score, reason = calculate_skill_score(
                candidate.candidate_id,
                job.job_id,
                db
            )

        elif criterion_type == "experience":

            score, reason = calculate_experience_score(
                candidate.candidate_id,
                job,
                db
            )

        elif criterion_type in [
            "qualification",
            "projects",
            "custom"
        ]:

            ai_result = ai_results.get(
                criterion.criteria_id
            )

            if ai_result:

                score = float(
                    ai_result["score"]
                )

                reason = ai_result["reason"]

            else:

                score = 0

                reason = (
                    "AI evaluation unavailable."
                )

        score = max(
            0,
            min(score, 100)
        )

        weighted_score = (
            score * criterion.weight
        ) / 100

        final_score += weighted_score

        results.append(
            {
                "criteria_id": criterion.criteria_id,
                "score": round(score, 2),
                "reason": reason
            }
        )

    return round(final_score, 2), results