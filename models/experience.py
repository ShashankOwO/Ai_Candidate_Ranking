from datetime import datetime,timezone
from sqlalchemy import Column,Integer,String,Text,Date,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Experience(Base):
    __tablename__="experience"

    experience_id=Column(Integer,primary_key=True,index=True)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    company_name=Column(String(150),nullable=False)
    job_title=Column(String(150),nullable=True)
    start_date=Column(Date,nullable=True)
    end_date=Column(Date,nullable=True)
    years=Column(Integer,nullable=True)
    description=Column(Text,nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)   
    )

    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    candidate=relationship("Candidate",back_populates="experiences")