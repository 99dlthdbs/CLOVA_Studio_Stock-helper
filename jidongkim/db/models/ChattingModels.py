from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import Relationship, relationship

from db import db
from db.models.BaseModel import BaseModel


class ChattingRoomModel(BaseModel):
    __tablename__ = "chatting_room"

    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")
    chats = relationship("ChattingModel", backref="chatting_room")


class ChattingModel(BaseModel):
    __tablename__ = "chatting"

    room_id = Column(Integer, ForeignKey("chatting_room.id"), nullable=False)
    chat_idx = Column(Integer, nullable=False)
    question = Column(String, nullable=True)
    answer = Column(String, nullable=True)
    card_data = Column(String, nullable=True)
    rag_data = Column(String, nullable=True)
    room = relationship("ChattingRoomModel", backref="chatting")
