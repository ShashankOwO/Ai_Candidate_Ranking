from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    job_title = Column(String(200), nullable=False)
    job_description = Column(String(1000))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)