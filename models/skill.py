from datetime import datetime,timezone

from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Skill(Base):
    __tablename__="skills"

    skill_id=Column(Integer,primary_key=True,index=True)
    Skill_name=Column(String(100),unique=True,nullable=False)
    skill_category=Column(String(100),nullable=False)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    candidate_skills=relationship("CandidateSkill",back_populates="skill")
    job_skills=relationship("JobSkill",back_populates="skill")
    










class CandidateSkill(Base):
    __tablename__="candidate_skills"

    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),primary_key=True)
    skill_id=Column(Integer,ForeignKey("skills.skill_id"),primary_key=True)
    proficiency=Column(String(50),nullable=True)
    years_experience=Column(Integer,nullable=True)

    skill=relationship("Skill",back_populates="candidate_skills")
    candidate=relationship("Candidate",back_populates="candidate_skills")


