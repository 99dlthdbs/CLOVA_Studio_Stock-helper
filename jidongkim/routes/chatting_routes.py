from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db_session
from db.models.ChattingModels import ChattingRoomModel, ChattingModel
from schemas.chatting_schemas import ChattingDisplay

router = APIRouter(
    prefix='/chatting',
    tags=['chatting']
)


@router.get('/{room_id}', response_model=list[ChattingDisplay])
def get_chatting(room_id: int, db: Session = Depends(get_db_session)):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    chat_list = [chat for chat in room.chats if chat.deleted_at is None]

    print(chat_list)

    return chat_list


@router.get('/{room_id}/latest', response_model=ChattingDisplay)
def get_lastest_chatting(room_id: int, db: Session = Depends(get_db_session)):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    chat_list = [chat for chat in room.chats if chat.deleted_at is None]

    return chat_list[-1]


def add_chat(room_id: int, question: str, answer: str, db: Session):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if not room:
        return "Room not found"

    chat_len = len(room.chats) + 1
    chat = ChattingModel(room_id=room_id, chat_idx=chat_len, question=question, answer=answer)

    db.add(chat)
    db.commit()

    return chat
