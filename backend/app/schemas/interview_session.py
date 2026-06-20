from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class ScreeningRequest(BaseModel):
    candidate_id: Optional[int] = Field(None, validation_alias=AliasChoices('candidate_id', 'candidateId'))
    candidate_name: Optional[str] = Field(None, validation_alias=AliasChoices('candidate_name', 'candidateName'))
    applied_role: Optional[str] = Field(None, validation_alias=AliasChoices('applied_role', 'appliedRole'))
    introduction: Optional[str] = Field(None, validation_alias=AliasChoices('introduction'))
    experience_years: str | int = Field(..., validation_alias=AliasChoices('experience_years', 'experienceYears', 'experience'))
    notice_period: str = Field(..., validation_alias=AliasChoices('notice_period', 'noticePeriod'))
    expected_salary: str = Field(..., validation_alias=AliasChoices('expected_salary', 'expectedSalary'))
    interested: bool = Field(..., validation_alias=AliasChoices('interested'))


class ScreeningResponse(BaseModel):
    qualification_score: int
    qualified: bool
    status: str

class InterviewSessionDatabase(BaseModel):
    id: int
    candidate_id: int
    introduction: Optional[str] = None
    experience_years: Optional[int] = None
    notice_period: Optional[str] = None
    expected_salary: Optional[str] = None
    interested: bool
    screening_score: int
    qualified: bool
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)
