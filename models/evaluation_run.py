from datetime import datetime,timezone

from sqlalchemy import(
    Column,Integer,String,DateTime,ForeignKey
)
from sqlalchemy.orm import relationship

from database import Base

class EvaluationRun(Base):
    __tablename__="evaluation_runs"

    evaluation_run_id=Column(Integer,primary_key=True,index=True)
    job_id=Column(Integer,ForeignKey("jobs.job_id"),nullable=False)
    run_name=Column(String(150),nullable=False)
    total_candidates=Column(Integer,nullable=False,default=0)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    job=relationship("Job",back_populates="evaluation_runs")
    results=relationship("EvaluationResult",back_populates="evaluation_run")
    rankings=relationship("CandidateRanking",back_populates="evaluation_run")

