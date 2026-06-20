from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.interview import InterviewRequest, InterviewResponse
from app.services.interview_service import schedule_interview

router = APIRouter()

@router.post(
    "/schedule-interview",
    response_model=InterviewResponse,
    summary="Schedule interview",
    description="Book a slot for a screened candidate and mark them as scheduled."
)
async def post_schedule_interview(req: InterviewRequest, db: AsyncSession = Depends(get_db)):
    return await schedule_interview(db, req)

