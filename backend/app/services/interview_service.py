from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.candidate import Candidate
from app.models.interview import Interview as DBInterview
from app.schemas.interview import InterviewRequest, InterviewResponse

async def schedule_interview(db: AsyncSession, req: InterviewRequest) -> InterviewResponse:
    # Resolve candidate by ID or Name
    candidate = None
    if req.candidate_id:
        stmt = select(Candidate).filter(Candidate.id == req.candidate_id)
        result = await db.execute(stmt)
        candidate = result.scalars().first()
    elif req.candidate_name:
        stmt = select(Candidate).filter(Candidate.name == req.candidate_name)
        result = await db.execute(stmt)
        candidate = result.scalars().first()
        if not candidate:
            stmt = select(Candidate).filter(Candidate.name.ilike(f"%{req.candidate_name}%"))
            result = await db.execute(stmt)
            candidate = result.scalars().first()

    if not candidate:
        if req.candidate_name:
            email_slug = req.candidate_name.lower().strip().replace(" ", "_")
            candidate = Candidate(
                name=req.candidate_name.strip(),
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
            identifier = req.candidate_id or "Unknown"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate '{identifier}' not found."
            )

    # Parse start_time
    start_time_dt = req.start_time
    if isinstance(start_time_dt, str):
        try:
            cleaned_str = start_time_dt.replace("Z", "+00:00")
            start_time_dt = datetime.fromisoformat(cleaned_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid start_time format '{start_time_dt}'. Must be ISO-8601."
            )

    interview_date = start_time_dt.date()
    interview_time = start_time_dt.time()

    # Create interview booking
    db_interview = DBInterview(
        candidate_id=candidate.id,
        interview_date=interview_date,
        interview_time=interview_time,
        status="Scheduled"
    )
    db.add(db_interview)

    # Update candidate status
    candidate.application_status = "Interview Scheduled"
    
    await db.commit()
    await db.refresh(db_interview)

    interview_id = f"INT-{1000 + db_interview.id}"

    return InterviewResponse(
        success=True,
        interview_id=interview_id,
        status="Interview Scheduled"
    )

