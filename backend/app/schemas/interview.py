from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class InterviewRequest(BaseModel):
    candidate_id: Optional[int] = Field(None, validation_alias=AliasChoices('candidate_id', 'candidateId'))
    candidate_name: Optional[str] = Field(None, validation_alias=AliasChoices('candidate_name', 'candidateName'))
    applied_role: Optional[str] = Field(None, validation_alias=AliasChoices('applied_role', 'appliedRole'))
    start_time: str | datetime = Field(..., validation_alias=AliasChoices('start_time', 'startTime'))


class InterviewResponse(BaseModel):
    success: bool
    interview_id: str
    status: str

class InterviewDatabase(BaseModel):
    id: int
    candidate_id: int
    interview_date: str
    interview_time: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
