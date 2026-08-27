from datetime import datetime,timezone
from sqlalchemy import(
    Column,Integer,DateTime,String,
    ForeignKey,UniqueConstraint,Float
)
from sqlalchemy.orm import relationship
from database import Base

class CandidateRanking(Base):
    __tablename__="candidate_rankings"

    __table_args__=(
        UniqueConstraint(
            "evaluation_run_id",
            "candidate_id",
            name="uq_candidate_ranking"
        ),
    )

    ranking_id=Column(Integer,primary_key=True,index=True)
    evaluation_run_id=Column(Integer,ForeignKey("evaluation_runs.evaluation_run_id"),nullable=False)
    candidate_id=Column(Integer,ForeignKey("candidates.candidate_id"),nullable=False)
    final_score=Column(Float,nullable=False)
    rank_position=Column(String(50),nullable=True)
    recommendation=Column(String(50),nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )
    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    evaluation_run=relationship("EvaluationRun",back_populates="rankings")
    candidate=relationship("Candidate",back_populates="rankings")
