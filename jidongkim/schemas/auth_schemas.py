from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ResponseLogin(BaseModel):
    email: str
    nickname: str


class ChatToken(BaseModel):
    token: str
    user_id: int
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
