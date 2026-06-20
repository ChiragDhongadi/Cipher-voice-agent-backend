from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    applied_role = Column(String, nullable=False)
    experience_years = Column(Integer, default=0, nullable=False)
    application_status = Column(String, default="Applied", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    interview_sessions = relationship("InterviewSession", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
