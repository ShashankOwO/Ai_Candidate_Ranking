from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class CandidateRanking(Base):
    __tablename__ = "candidate_rankings"

    ranking_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    candidate_id = Column(
        BigInteger,
        ForeignKey("candidates.candidate_id"),
        nullable=False
    )

    evaluation_run_id = Column(
        BigInteger,
        ForeignKey("evaluation_run.evaluation_run_id"),
        nullable=False
    )

    criteria_id = Column(
        BigInteger,
        ForeignKey("evaluation_criteria.criteria_id"),
        nullable=False
    )

    final_score = Column(BigInteger)

    rank_position = Column(BigInteger)

    recommendation = Column(String(100))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )