from datetime import datetime,timezone
from sqlalchemy import Column,Integer,String,Text,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Resume(Base):
    __table__="resumes"

    resume_id=Column(Integer,primary_key=True,index=True)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    filename=Column(String(50),nullable=False)
    file_type=Column(String(50),nullable=False)
    file_size=Column(Integer,nullable=False)
    raw_text=Column(Text,nullable=True)

    uploaded_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    candidate=relationship("Candidate",back_populates="resumes")