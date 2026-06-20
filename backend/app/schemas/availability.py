from typing import List
from pydantic import BaseModel

class AvailabilityResponse(BaseModel):
    available_slots: List[str]
