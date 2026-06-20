from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    introduction = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    notice_period = Column(String, nullable=True)
    expected_salary = Column(String, nullable=True)
    interested = Column(Boolean, default=True, nullable=False)
    screening_score = Column(Integer, nullable=False)
    qualified = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    candidate = relationship("Candidate", back_populates="interview_sessions")
