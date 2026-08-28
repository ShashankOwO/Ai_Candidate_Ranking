from sqlalchemy.orm import Session

from models.candidate import Candidate
from models.skill import Skill,CandidateSkill
from models.job import JobSkill,Job
from models.experience import Experience
from models.qualification import Qualification
from models.project import Project
from models.evaluation import EvaluationCriteria



def caluclate_skill_score(candidate_id:int,job_id:int,db:Session)->tuple[float,str]:

    job_skills=(db.query(JobSkill,Skill).join(Skill,JobSkill.skill_id==Skill.skill_id).filter(JobSkill.job_id==job_id)).all()

    if not job_skills:
        return 0,"No job skills configured"

    candidate_skill_map={skill.skill_name.lower():candidate_skill for candidate_skill,skill in candidate_skills}

    total_score=0
    total_weight=0
    matched_skills=[]
    missing_skills=[]

    for job_skill,skill in job_skills:

        if job_skill.skill_type=="required":
            skill_weight=2
        else:
            skill_weight=1

        total_weight+=skill_weight

        if skill.skill_name.lower() in candidate_skill_map:
            total_score+=skill_weight
            matched_skills.append(skill.skill_name)

        else:
            missing_skills.append(skill.skill_name)


    if total_weight==0:
        return 0,"No skills available for evaluation"

    score=(total_score/total_weight)*100

    reason=(
        f"Matched skills:{', '.join(matched_skills) or 'None'}"
        f"Misiing skills:{', '.join(missing_skills) or 'None'}"
    )

    return round(score,2),reason




def caluclate_experience_score(candidate_id:int,job:Job,db:Session)->tuple[float,str]:

    experiences=db.query(Experience).filter(Experience.candidate_id==candidate_id).all()

    if not experiences:
        return 0,"No professional experience found."

    total_years=sum(experience.years or 0 for experience in experiences)

    required_years=job.minimum_experience or 0

    if required_years==0:
        return 100,"No minimum experience requirement"

    score=(total_years/required_years)*100

    if score>100:
        score=100

    reason=(
        f"Candidate has {total_years} years of experience"
        f"Job requires {required_years} years"
    )

    return round(score,2),reason





def caluclate_qualification_score(candidate_id:int,db:Session)->tuple[float,str]:

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


def caluclate_project_score(candidate_id:int,db:Session)->tuple[float,str]:

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





def caluclate_candidate_score(candidate:Candidate,job:Job,criteria:list[EvaluationCriteria],db:Session):

    results=[]

    final_score=0

    for criterion in criteria:

        score=0
        reason=""

        if criterion.criteria_type=="skills":
            score,reason=caluclate_skill_score(candidate.candidate_id,job.job_id,db)

        elif criterion.criteria_type=="experience":
            score,reason=caluclate_experience_score(Candidate.candidate_id,job,db)

        elif criterion.criteria_type=="qualification":
            score,reason=caluclate_qualification_score(candidate.candidate_id,db)

        elif criterion.criteria_type=="projects":
            score,reason=caluclate_project_score(candidate.candidate_id,db)

        elif criterion.criteria_type=="custom":

            score=0
            reason="Custom AI evaluation pending"

        weighted_score=(score/criterion.max_score)*criterion.weight

        final_score+=weighted_score

        results.append({
            "criteria_id":criterion.criteria_id,
            "score":round(score,2),
            "reason":reason
        })

    return round(final_score,2),results


