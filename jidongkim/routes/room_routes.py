from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.db import get_db_session
from db.models.ChattingModels import ChattingRoomModel
from schemas.room_schemas import RoomDisplay, RoomCreate

router = APIRouter(prefix='/room', tags=['room'])


@router.get('/', response_model=List[RoomDisplay])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    rooms = db.query(ChattingRoomModel).filter(ChattingRoomModel.deleted_at.is_(None)).offset(skip).limit(limit).all()
    return rooms


@router.post('/', response_model=RoomDisplay)
def create_room(room: RoomCreate, db: Session = Depends(get_db_session)):
    db_room = ChattingRoomModel(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.delete('/{room_id}', response_model=RoomDisplay)
def delete_room(room_id: int, db: Session = Depends(get_db_session)):
    room = db.query(ChattingRoomModel).filter(ChattingRoomModel.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.deleted_at = datetime.now()
    db.commit()
    return room
