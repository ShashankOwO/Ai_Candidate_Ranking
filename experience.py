from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, FLOAT
from database import Base

class Experience(Base):
    __tablename__ = "experience"

    experience_id = Column(BigInteger, primary_key=True)
    candidate_id = Column(BigInteger, ForeignKey("candidates.candidate_id"), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_title = Column(String(100), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    years = Column(FLOAT)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)