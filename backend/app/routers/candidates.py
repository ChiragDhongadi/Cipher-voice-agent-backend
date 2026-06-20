from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateProfileResponse, CandidateProfileRequest

router = APIRouter()

async def query_candidate_profile(db: AsyncSession, c_id: Optional[str], c_name: Optional[str]) -> CandidateProfileResponse:
    candidate = None
    if c_id:
        try:
            val_id = int(c_id)
            stmt = select(Candidate).filter(Candidate.id == val_id)
            result = await db.execute(stmt)
            candidate = result.scalars().first()
        except ValueError:
            pass

    if not candidate and c_name:
        stmt = select(Candidate).filter(Candidate.name == c_name)
        result = await db.execute(stmt)
        candidate = result.scalars().first()
        if not candidate:
            stmt = select(Candidate).filter(Candidate.name.ilike(f"%{c_name}%"))
            result = await db.execute(stmt)
            candidate = result.scalars().first()

    if not candidate:
        if c_name:
            email_slug = c_name.lower().strip().replace(" ", "_")
            candidate = Candidate(
                name=c_name.strip(),
                email=f"{email_slug}@example.com",
                phone="Unknown",
                applied_role="AI Engineer",
                experience_years=0,
                application_status="Applied"
            )
            db.add(candidate)
            await db.commit()
            await db.refresh(candidate)
        else:
            identifier = c_id or "Unknown"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate '{identifier}' not found."
            )

    # Check if they have an active/updated experience in an interview session
    from app.models.interview_session import InterviewSession
    stmt = select(InterviewSession).filter(InterviewSession.candidate_id == candidate.id).order_by(InterviewSession.id.desc())
    result = await db.execute(stmt)
    latest_session = result.scalars().first()
    exp_years = latest_session.experience_years if latest_session and latest_session.experience_years is not None else candidate.experience_years
    experience_str = f"{exp_years} years"

    return CandidateProfileResponse(
        candidate_name=candidate.name,
        applied_role=candidate.applied_role,
        experience=experience_str,
        email=candidate.email,
        phone=candidate.phone,
        status=candidate.application_status
    )

@router.get(
    "/candidate-profile/{candidate_id}",
    response_model=CandidateProfileResponse,
    summary="Get candidate profile by path parameter",
    description="Retrieve details of a candidate by their ID."
)
async def get_candidate_profile(candidate_id: int, db: AsyncSession = Depends(get_db)):
    return await query_candidate_profile(db, str(candidate_id), None)

@router.get(
    "/candidate-profile",
    response_model=CandidateProfileResponse,
    summary="Get candidate profile by query parameter",
    description="Retrieve details of a candidate using query parameter candidate_id or candidate_name."
)
async def get_candidate_profile_query(
    candidate_id: Optional[str] = None,
    candidate_name: Optional[str] = None,
    candidateId: Optional[str] = None,
    candidateName: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    c_id = candidate_id or candidateId
    c_name = candidate_name or candidateName
    return await query_candidate_profile(db, c_id, c_name)

@router.post(
    "/candidate-profile",
    response_model=CandidateProfileResponse,
    summary="Get candidate profile by POST body",
    description="Retrieve details of a candidate using a POST request body."
)
async def post_candidate_profile(
    req: CandidateProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    return await query_candidate_profile(db, req.candidate_id, req.candidate_name)


