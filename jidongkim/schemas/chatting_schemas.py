from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChattingDisplay(BaseModel):
    id: int
    room_id: int
    chat_idx: int
    question: str
    answer: str
    card_data: str
    rag_data: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True
