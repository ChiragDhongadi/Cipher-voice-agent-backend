from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.interview_session import ScreeningRequest, ScreeningResponse
from app.services.screening_service import screen_candidate

router = APIRouter()

@router.post(
    "/screen-candidate",
    response_model=ScreeningResponse,
    summary="Screen candidate and log session info",
    description="Save candidate responses, introduction, technical answers, compute qualification score, and determine threshold status."
)
async def post_screen_candidate(req: ScreeningRequest, db: AsyncSession = Depends(get_db)):
    return await screen_candidate(db, req)

