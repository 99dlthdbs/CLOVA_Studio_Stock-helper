import os
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import JWTError, jwt
from typing import Optional

import bcrypt

from db.db import get_db_session
from db.models import AuthModels
from schemas import auth_schemas

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/auth", tags=["auth"])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode(
        "utf-8"
    )  # Convert bytes to string before storing in the database


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode(
        "utf-8"
    )  # Convert string to bytes before checking
    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password_bytes
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return payload


def get_user_from_token(token: str, db: Session = Depends(get_db_session)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(AuthModels.User).filter(AuthModels.User.username == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(request: Request, db: Session = Depends(get_db_session)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    access_token = access_token.replace("Bearer ", "")
    payload = decode_access_token(access_token)
    user = (
        db.query(AuthModels.User)
        .filter(AuthModels.User.username == payload.get("sub"))
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/signup", response_model=auth_schemas.User)
def create_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db_session)):
    db_user = (
        db.query(AuthModels.User).filter(AuthModels.User.email == user.email).first()
    )
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    hashed_password = hash_password(user.password)
    db_user = AuthModels.User(
        email=user.email, password=hashed_password, nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=auth_schemas.ResponseLogin)
async def login_for_access_token(
    user: auth_schemas.UserLogin,
    db: Session = Depends(get_db_session),
    response: Response = None,
):
    db_user = (
        db.query(AuthModels.User).filter(AuthModels.User.email == user.email).first()
    )

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": db_user.email})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="none",
    )

    return {"data": True}


@router.get("/me", response_model=auth_schemas.User)
def read_users_me(current_user: auth_schemas.User = Depends(get_current_user)):
    return current_user


@router.delete("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"data": "Logged out"}


@router.get("/isLogged")
def is_logged(request: Request):
    access_token = request.cookies.get("access_token")
    print(request.cookies)
    if not access_token:
        return {"isLogged": False}
    return {"isLogged": True}
