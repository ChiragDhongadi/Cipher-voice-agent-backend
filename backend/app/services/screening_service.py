import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.candidate import Candidate
from app.models.interview_session import InterviewSession as DBInterviewSession
from app.schemas.interview_session import ScreeningRequest, ScreeningResponse


def parse_salary(salary_str: str) -> float | None:
    """Extracts numerical salary value from string (e.g. '8 LPA' -> 8.0)."""
    matches = re.findall(r"\d+(?:\.\d+)?", salary_str)
    if matches:
        return float(matches[0])
    return None

def parse_notice_period(notice_str: str) -> int:
    """Extracts notice period in days from string (e.g. '30 days' -> 30)."""
    notice_str_lower = notice_str.lower()
    if "immediate" in notice_str_lower:
        return 0

    matches = re.findall(r"\d+", notice_str_lower)
    if matches:
        days = int(matches[0])
        if "month" in notice_str_lower:
            days = days * 30
        return days

    return 30

def calculate_score(
    experience_years: int, notice_period: str, expected_salary: str, interested: bool
) -> tuple[int, bool]:
    """Calculates screening score and qualification status."""
    if not interested:
        return 0, False

    score = 20

    # Experience points: 15 per year (max 45)
    exp_points = min(experience_years * 15, 45)
    score += exp_points

    # Notice Period points
    days = parse_notice_period(notice_period)
    if days <= 15:
        score += 30
    elif days <= 30:
        score += 20
    elif days <= 60:
        score += 10
    else:
        score += 0

    # Expected Salary points
    salary = parse_salary(expected_salary)
    if salary is not None:
        if salary <= 8.0:
            score += 25
        elif salary <= 12.0:
            score += 20
        elif salary <= 15.0:
            score += 10
        else:
            score += 5
    else:
        score += 15

    score = min(score, 100)
    qualified = score >= 70
    return score, qualified

async def screen_candidate(db: AsyncSession, req: ScreeningRequest) -> ScreeningResponse:
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

    # Convert experience_years to int
    try:
        exp_years = int(req.experience_years)
    except ValueError:
        exp_years = 0

    # Calculate score
    score, qualified = calculate_score(
        exp_years, req.notice_period, req.expected_salary, req.interested
    )

    # Save to InterviewSession
    db_session = DBInterviewSession(
        candidate_id=candidate.id,
        introduction=req.introduction,
        experience_years=exp_years,
        notice_period=req.notice_period,
        expected_salary=req.expected_salary,
        interested=req.interested,
        screening_score=score,
        qualified=qualified
    )
    db.add(db_session)

    # Update candidate status based on score
    if qualified:
        candidate.application_status = "Screened - Qualified"
        status_msg = "Screened - Qualified"
    else:
        candidate.application_status = "Screened - Unqualified"
        status_msg = "Screened - Unqualified"

    await db.commit()
    await db.refresh(db_session)

    return ScreeningResponse(
        qualification_score=score,
        qualified=qualified,
        status=status_msg
    )

