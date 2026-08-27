from datetime import datetime,timezone
from sqlalchemy import Column,ForeignKey,Integer,Text,Float,DateTime,String
from sqlalchemy.orm import relationship
from database import Base

class Qualification(Base):
    __tablename__="qualifications"

    qualification_id=Column(Integer,primary_key=True,index=True)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    university=Column(String(200),nullable=True)
    degree=Column(String(100),nullable=True)
    specialization=Column(String(150),nullable=True)
    percentage=Column(Float,nullable=True)
    passed_out_year=Column(Integer,nullable=True)
    joining_year=Column(Integer,nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )
    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    candidate=relationship("Candidate",back_populates="qualifications")
