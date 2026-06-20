from typing import Optional
from fastapi import APIRouter
from app.schemas.availability import AvailabilityResponse

router = APIRouter()

@router.get(
    "/check-availability",
    response_model=AvailabilityResponse,
    summary="Check available interview slots",
    description="Get available interview slots."
)
async def check_availability(date: Optional[str] = None):
    return AvailabilityResponse(
        available_slots=[
            "10:00 AM",
            "11:00 AM",
            "02:00 PM",
            "04:00 PM"
        ]
    )

