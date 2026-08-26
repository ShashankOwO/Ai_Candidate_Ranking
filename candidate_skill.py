from sqlalchemy import Column, BigInteger, ForeignKey
from database import Base

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    candidate_id = Column(
        BigInteger,
        ForeignKey("candidates.candidate_id"),
        primary_key=True
    )

    skill_id = Column(
        BigInteger,
        ForeignKey("skills.skill_id"),
        primary_key=True
    )