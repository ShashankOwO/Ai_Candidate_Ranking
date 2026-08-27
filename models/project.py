from datetime import datetime,timezone

from sqlalchemy import Column,Integer,String,Text,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__="projects"

    project_id=Column(Integer,primary_key=True,index=True)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    project_name=Column(String(200),nullable=False)
    description=Column(Text,nullable=False)
    technologies=Column(Text,nullable=True)
    role=Column(String(150),nullable=True)
    duration=Column(String(100),nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    candidate=relationship("Candidate",back_populates="projects")