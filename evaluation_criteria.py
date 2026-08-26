from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class EvaluationCriteria(Base):
    __tablename__ = "evaluation_criteria"

    criteria_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    job_id = Column(
        BigInteger,
        ForeignKey("jobs.job_id"),
        nullable=False
    )

    criteria_name = Column(
        String(100),
        nullable=False
    )

    criteria_type = Column(
        String(100)
    )

    weight = Column(BigInteger)

    max_score = Column(BigInteger)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )