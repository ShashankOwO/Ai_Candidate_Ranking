from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey,Float
from database import Base

class Qualification(Base):
    __tablename__ = "qualification"

    qualification_id = Column(BigInteger, primary_key=True)
    candidate_id = Column(BigInteger, ForeignKey("candidates.candidate_id"), nullable=False)
    education_institute = Column(String(200), nullable=False)
    degree = Column(String(100), nullable=False)
    branch = Column(String(100))
    percentage = Column(Float)
    passed_out_year = Column(BigInteger)
    joining_year = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)