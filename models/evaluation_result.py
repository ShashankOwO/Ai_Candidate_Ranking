from datetime import datetime,timezone
from sqlalchemy import(
    Column,
    Integer,
    Float,
    Text,DateTime,ForeignKey
)
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class EvaluationResult(Base):
    __tablename__="evaluation_results"

    __table_args__ = (
        UniqueConstraint(
            "evaluation_run_id",
            "candidate_id",
            "criteria_id",
            name="uq_evaluation_result"
        ),
    )

    result_id=Column(Integer,primary_key=True,index=True)
    evaluation_run_id=Column(Integer,ForeignKey("evaluation_runs.evaluation_run_id"),nullable=False)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    criteria_id=Column(Integer,ForeignKey("evaluation_criteria.criteria_id"),nullable=False)
    score=Column(Float,nullable=False)
    reason=Column(Text,nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    evaluation_run=relationship("EvaluationRun",back_populates="results")
    candidate=relationship("Candidate",back_populates="evaluation_results")
    criteria=relationship("EvaluationCriteria",back_populates="results")

