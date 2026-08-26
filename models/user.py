from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime,timezone
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__="users"

    user_id=Column(Integer,primary_key=True,index=True)
    username=Column(String(50),unique=True,nullable=False)
    email=Column(String(100),unique=True,nullable=False)
    password=Column(String(255),nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    candidates=relationship("Candidate",back_populates="user")
    jobs=relationship("Job",back_populates="user")
    


    

