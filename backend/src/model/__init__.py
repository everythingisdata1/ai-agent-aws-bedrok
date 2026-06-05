from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
