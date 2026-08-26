from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_run"

    evaluation_run_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    job_id = Column(
        BigInteger,
        ForeignKey("jobs.job_id"),
        nullable=False
    )

    run_name = Column(
        String(100),
        nullable=False
    )

    total_candidates = Column(BigInteger)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )