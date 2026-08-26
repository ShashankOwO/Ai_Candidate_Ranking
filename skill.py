from sqlalchemy import Column, BigInteger, String, DateTime
from database import Base

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(BigInteger, primary_key=True)
    skill_name = Column(String(100), nullable=False)
    skill_category = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)