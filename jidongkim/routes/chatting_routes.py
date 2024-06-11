from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db_session
from db.models.ChattingModels import ChattingRoomModel, ChattingModel
from db.models import AuthModels
from schemas.auth_schemas import ChatToken
from routes.auth_routes import create_access_token, get_current_user
from schemas.chatting_schemas import ChattingDisplay

router = APIRouter(prefix="/api/chatting", tags=["chatting"])


@router.get("/token/{room_id}", response_model=ChatToken)
def get_chat_token(
    room_id: int, db: Session = Depends(get_db_session), user=Depends(get_current_user)
):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if room.owner_id != user.id:
        raise HTTPException(status_code=401, detail="Not authorized")

    expires_at = datetime.utcnow() + timedelta(minutes=15)

    token = AuthModels.ChatToken(
        token=create_access_token(
            {
                "email": user.email,
                "room_id": room_id,
                "exp": expires_at,
            }
        ),
        user_id=user.id,
        expires_at=expires_at,
    )

    db.add(token)
    db.commit()

    return token


@router.get("/{room_id}", response_model=list[ChattingDisplay])
def get_chatting(
    room_id: int, db: Session = Depends(get_db_session), user=Depends(get_current_user)
):
    room = (
        db.query(ChattingRoomModel)
        .filter(ChattingRoomModel.owner_id == user.id)
        .filter(ChattingRoomModel.id == room_id)
        .first()
    )

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    chat_list = [chat for chat in room.chats if chat.deleted_at is None]

    print(chat_list)

    return chat_list


@router.get("/{room_id}/latest", response_model=ChattingDisplay)
def get_lastest_chatting(
    room_id: int, db: Session = Depends(get_db_session), user=Depends(get_current_user)
):
    room = (
        db.query(ChattingRoomModel)
        .filter(ChattingRoomModel.owner_id == user.id)
        .filter(ChattingRoomModel.id == room_id)
        .first()
    )

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    chat_list = [chat for chat in room.chats if chat.deleted_at is None]

    return chat_list[-1]


def add_chat(
    room_id: int,
    question: str,
    answer: str,
    db: Session,
    user: AuthModels.User,
    card_data: list[str] = None,
    rag_data: str = None,
):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if room.owner_id != user.id:
        return "Not authorized"

    if not room:
        return "Room not found"

    chat_len = len(room.chats) + 1

    card_data_str = "%T%T%".join(card_data) if card_data else None

    chat = ChattingModel(
        room_id=room_id,
        chat_idx=chat_len,
        question=question,
        answer=answer,
        card_data=card_data_str,
        rag_data=rag_data,
    )

    db.add(chat)
    db.commit()

    return chat
