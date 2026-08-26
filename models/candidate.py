from datetime import datetime,timezone
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Candidate(Base):
    __tablename__="candidates"

    candidate_id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.user_id"),nullable=False)
    full_name=Column(String(100),nullable=False)
    contact_no=Column(String(20),nullable=True)
    email_address=Column(String(100),nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user=relationship("User",back_populates="candidates")
    resumes=relationship("Resume",back_populates="candidate")
