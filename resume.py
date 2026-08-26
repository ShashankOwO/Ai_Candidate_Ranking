from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from database import Base

class Resume(Base):
    __tablename__ = "resume"

    resume_id = Column(BigInteger, primary_key=True)
    candidate_id = Column(BigInteger, ForeignKey("candidates.candidate_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime)
    file_type = Column(String(50))
    file_size = Column(String(50))
    raw_text = Column(String)
    updated_at = Column(DateTime)