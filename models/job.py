from datetime import datetime,timezone
from sqlalchemy import(
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base

class Job(Base):
    __tablename__="jobs"

    job_id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.user_id"),nullable=False)
    job_title=Column(String(150),nullable=False)
    job_description=Column(Text,nullable=False)
    minimum_experience=Column(Integer,nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


    user=relationship("User",back_populates="jobs")
    job_skills=relationship("JobSkill",back_populates="job")
    evaluation_criteria = relationship("EvaluationCriteria",back_populates="job")
    evaluation_runs=relationship("EvaluationRun",back_populates="job")











class JobSkill(Base):
    __tablename__="job_skills"

    job_id=Column(Integer,ForeignKey("jobs.job_id"),primary_key=True)
    skill_id=Column(Integer,ForeignKey("skills.skill_id"),primary_key=True)
    skill_type=Column(String(20),nullable=False)

    job=relationship("Job",back_populates="job_skills")
    skill=relationship("Skill",back_populates="job_skills")