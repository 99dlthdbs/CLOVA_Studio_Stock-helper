from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from db.models.BaseModel import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
