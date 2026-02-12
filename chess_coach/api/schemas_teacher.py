from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class TodayPlanRequest(BaseModel):
    username: str
    minutes: int = Field(45, ge=10, le=180)
    fatigue: Optional[int] = Field(None, ge=0, le=10)
