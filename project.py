from sqlalchemy import Column, BigInteger, String, ForeignKey
from database import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(BigInteger, primary_key=True)
    candidate_id = Column(BigInteger, ForeignKey("candidates.candidate_id"), nullable=False)
    project_name = Column(String(200), nullable=False)
    technologies = Column(String(500), nullable=False)