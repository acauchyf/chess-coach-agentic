from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class ChatRequest(BaseModel):
    username: str
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    reply: str
    fatigue: Optional[int] = None
    plan: Optional[Dict[str, Any]] = None
