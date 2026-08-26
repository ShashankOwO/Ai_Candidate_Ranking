from sqlalchemy import Column, BigInteger, String, ForeignKey
from database import Base

class JobSkill(Base):
    __tablename__ = "job_skills"

    skill_id = Column(BigInteger, ForeignKey("skills.skill_id"), primary_key=True)
    job_id = Column(BigInteger, ForeignKey("jobs.job_id"), primary_key=True)
    skill_type = Column(String(100))