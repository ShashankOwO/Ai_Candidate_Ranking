from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    contact_no = Column(
        String(20),
        nullable=False
    )

    email_address = Column(
        String(150),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )