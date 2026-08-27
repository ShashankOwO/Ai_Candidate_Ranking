from datetime import datetime,timezone

from sqlalchemy import(
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base

class EvaluationCriteria(Base):
    __tablename__="evaluation_criteria"

    criteria_id=Column(Integer,primary_key=True,index=True)
    job_id=Column(Integer,ForeignKey("jobs.job_id"),nullable=False)
    criteria_name=Column(String(100),nullable=False)
    criteria_type=Column(String(50),nullable=False)
    criteria_description=Column(Text,nullable=True)
    weight=Column(Float,nullable=False)
    max_score=Column(Float,nullable=False,default=100)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )


    job=relationship("Job",back_populates="evaluation_criteria")
    results=relationship("EvaluationResult",back_populates="criteria")
