from sqlalchemy import Column, String

from db import db
from db.models.BaseModel import BaseModel


class ChattingRoomModel(BaseModel):
    __tablename__ = 'chatting_rooms'

    name = Column(String, nullable=False)