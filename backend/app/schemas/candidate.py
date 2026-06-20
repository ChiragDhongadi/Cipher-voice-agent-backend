from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class CandidateBase(BaseModel):
    name: str
    email: str
    phone: str
    applied_role: str

class CandidateCreate(CandidateBase):
    pass

class CandidateSchema(CandidateBase):
    id: int
    application_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileResponse(BaseModel):
    candidate_name: str
    applied_role: str
    experience: str
    email: str
    phone: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileRequest(BaseModel):
    candidate_id: Optional[str] = Field(None, validation_alias=AliasChoices('candidate_id', 'candidateId'))
    candidate_name: Optional[str] = Field(None, validation_alias=AliasChoices('candidate_name', 'candidateName'))

