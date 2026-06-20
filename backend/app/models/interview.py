from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    interview_date = Column(Date, nullable=False)
    interview_time = Column(Time, nullable=False)
    status = Column(String, default="Scheduled", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    candidate = relationship("Candidate", back_populates="interviews")
