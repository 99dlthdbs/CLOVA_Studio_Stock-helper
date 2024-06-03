from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db_session
from db.models.ChattingModels import ChattingRoomModel
from routes.auth_routes import get_current_user
from schemas.room_schemas import RoomDisplay, RoomCreate

router = APIRouter(prefix="/room", tags=["room"])


@router.get("/", response_model=List[RoomDisplay])
def read_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    rooms = (
        db.query(ChattingRoomModel)
        .filter(ChattingRoomModel.owner_id == user.id)
        .filter(ChattingRoomModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rooms


@router.post("/", response_model=RoomDisplay)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    db_room = ChattingRoomModel(name=room.name, owner_id=user.id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.delete("/{room_id}", response_model=RoomDisplay)
def delete_room(
    room_id: int, db: Session = Depends(get_db_session), user=Depends(get_current_user)
):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    room.deleted_at = datetime.now()
    db.commit()
    return room
