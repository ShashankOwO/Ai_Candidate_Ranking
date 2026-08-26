from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import Base, engine, get_db

from user import User
from candidate import Candidate
from project import Project
from resume import Resume
from qualification import Qualification
from skill import Skill
from candidate_skill import CandidateSkill
from experience import Experience
from job import Job
from job_skill import JobSkill
from evaluation_criteria import EvaluationCriteria
from evaluation_run import EvaluationRun
from candidate_ranking import CandidateRanking


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Candidate Ranking Engine",
    version="1.0.0"
)



@app.get("/")
def home():
    return {
        "message": "AI Candidate Ranking Engine API is running"
    }




@app.post("/users")
def create_user(
    user_name: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        user_name=user_name,
        email=email,
        password=password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}




@app.post("/candidates")
def create_candidate(
    user_id: int,
    full_name: str,
    contact_no: str,
    email_address: str,
    db: Session = Depends(get_db)
):
    candidate = Candidate(
        user_id=user_id,
        full_name=full_name,
        contact_no=contact_no,
        email_address=email_address
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


@app.get("/candidates")
def get_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()


@app.get("/candidates/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate


@app.delete("/candidates/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.candidate_id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted successfully"}



@app.post("/projects")
def create_project(
    candidate_id: int,
    project_name: str,
    technologies: str,
    db: Session = Depends(get_db)
):
    project = Project(
        candidate_id=candidate_id,
        project_name=project_name,
        technologies=technologies
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/candidates/{candidate_id}/projects")
def get_candidate_projects(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Project).filter(
        Project.candidate_id == candidate_id
    ).all()


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.project_id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}




@app.post("/resumes")
def create_resume(
    candidate_id: int,
    file_name: str,
    file_path: str,
    file_type: str,
    file_size: str,
    raw_text: str,
    db: Session = Depends(get_db)
):
    resume = Resume(
        candidate_id=candidate_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        raw_text=raw_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@app.get("/resumes")
def get_resumes(db: Session = Depends(get_db)):
    return db.query(Resume).all()


@app.get("/candidates/{candidate_id}/resume")
def get_candidate_resume(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Resume).filter(
        Resume.candidate_id == candidate_id
    ).all()




@app.post("/qualifications")
def create_qualification(
    candidate_id: int,
    education_institute: str,
    degree: str,
    branch: str,
    percentage: float,
    passed_out_year: int,
    joining_year: int,
    db: Session = Depends(get_db)
):
    qualification = Qualification(
        candidate_id=candidate_id,
        education_institute=education_institute,
        degree=degree,
        branch=branch,
        percentage=percentage,
        passed_out_year=passed_out_year,
        joining_year=joining_year
    )

    db.add(qualification)
    db.commit()
    db.refresh(qualification)

    return qualification


@app.get("/candidates/{candidate_id}/qualifications")
def get_qualifications(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Qualification).filter(
        Qualification.candidate_id == candidate_id
    ).all()



@app.post("/skills")
def create_skill(
    skill_name: str,
    skill_category: str,
    db: Session = Depends(get_db)
):
    skill = Skill(
        skill_name=skill_name,
        skill_category=skill_category
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


@app.get("/skills")
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()


@app.get("/skills/{skill_id}")
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(
        Skill.skill_id == skill_id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    return skill


@app.post("/candidate-skills")
def add_candidate_skill(
    candidate_id: int,
    skill_id: int,
    db: Session = Depends(get_db)
):
    candidate_skill = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_id
    )

    db.add(candidate_skill)
    db.commit()

    return {
        "message": "Skill added to candidate successfully"
    }


@app.get("/candidates/{candidate_id}/skills")
def get_candidate_skills(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(CandidateSkill).filter(
        CandidateSkill.candidate_id == candidate_id
    ).all()




@app.post("/experiences")
def create_experience(
    candidate_id: int,
    company_name: str,
    job_title: str,
    years: float,
    db: Session = Depends(get_db)
):
    experience = Experience(
        candidate_id=candidate_id,
        company_name=company_name,
        job_title=job_title,
        years=years
    )

    db.add(experience)
    db.commit()
    db.refresh(experience)

    return experience


@app.get("/candidates/{candidate_id}/experiences")
def get_experiences(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Experience).filter(
        Experience.candidate_id == candidate_id
    ).all()



@app.post("/jobs")
def create_job(
    user_id: int,
    job_title: str,
    job_description: str,
    db: Session = Depends(get_db)
):
    job = Job(
        user_id=user_id,
        job_title=job_title,
        job_description=job_description
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@app.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}


@app.post("/job-skills")
def add_job_skill(
    job_id: int,
    skill_id: int,
    skill_type: str,
    db: Session = Depends(get_db)
):
    job_skill = JobSkill(
        job_id=job_id,
        skill_id=skill_id,
        skill_type=skill_type
    )

    db.add(job_skill)
    db.commit()

    return {
        "message": "Skill added to job successfully"
    }


@app.get("/jobs/{job_id}/skills")
def get_job_skills(
    job_id: int,
    db: Session = Depends(get_db)
):
    return db.query(JobSkill).filter(
        JobSkill.job_id == job_id
    ).all()



@app.post("/evaluation-criteria")
def create_evaluation_criteria(
    job_id: int,
    criteria_name: str,
    criteria_type: str,
    weight: float,
    max_score: float,
    db: Session = Depends(get_db)
):
    criteria = EvaluationCriteria(
        job_id=job_id,
        criteria_name=criteria_name,
        criteria_type=criteria_type,
        weight=weight,
        max_score=max_score
    )

    db.add(criteria)
    db.commit()
    db.refresh(criteria)

    return criteria


@app.get("/evaluation-criteria")
def get_evaluation_criteria(
    db: Session = Depends(get_db)
):
    return db.query(EvaluationCriteria).all()


@app.get("/jobs/{job_id}/criteria")
def get_job_criteria(
    job_id: int,
    db: Session = Depends(get_db)
):
    return db.query(EvaluationCriteria).filter(
        EvaluationCriteria.job_id == job_id
    ).all()


@app.post("/evaluation-runs")
def create_evaluation_run(
    job_id: int,
    run_name: str,
    total_candidates: int,
    db: Session = Depends(get_db)
):
    evaluation_run = EvaluationRun(
        job_id=job_id,
        run_name=run_name,
        total_candidates=total_candidates
    )

    db.add(evaluation_run)
    db.commit()
    db.refresh(evaluation_run)

    return evaluation_run


@app.get("/evaluation-runs")
def get_evaluation_runs(
    db: Session = Depends(get_db)
):
    return db.query(EvaluationRun).all()


@app.get("/jobs/{job_id}/evaluation-runs")
def get_job_evaluation_runs(
    job_id: int,
    db: Session = Depends(get_db)
):
    return db.query(EvaluationRun).filter(
        EvaluationRun.job_id == job_id
    ).all()




@app.post("/candidate-rankings")
def create_candidate_ranking(
    candidate_id: int,
    evaluation_run_id: int,
    criteria_id: int,
    final_score: float,
    rank_position: int,
    recommendation: str,
    db: Session = Depends(get_db)
):
    ranking = CandidateRanking(
        candidate_id=candidate_id,
        evaluation_run_id=evaluation_run_id,
        criteria_id=criteria_id,
        final_score=final_score,
        rank_position=rank_position,
        recommendation=recommendation
    )

    db.add(ranking)
    db.commit()
    db.refresh(ranking)

    return ranking


@app.get("/candidate-rankings")
def get_candidate_rankings(
    db: Session = Depends(get_db)
):
    return db.query(CandidateRanking).order_by(
        CandidateRanking.rank_position
    ).all()


@app.get("/jobs/{job_id}/rankings")
def get_job_rankings(
    job_id: int,
    db: Session = Depends(get_db)
):
    rankings = (
        db.query(CandidateRanking)
        .join(
            EvaluationRun,
            CandidateRanking.evaluation_run_id
            == EvaluationRun.evaluation_run_id
        )
        .filter(EvaluationRun.job_id == job_id)
        .order_by(CandidateRanking.rank_position)
        .all()
    )

    return rankings


@app.get("/candidates/{candidate_id}/rankings")
def get_candidate_rankings_by_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    rankings = db.query(CandidateRanking).filter(
        CandidateRanking.candidate_id == candidate_id
    ).order_by(
        CandidateRanking.rank_position
    ).all()

    if not rankings:
        raise HTTPException(
            status_code=404,
            detail="Rankings not found for this candidate"
        )

    return rankings
