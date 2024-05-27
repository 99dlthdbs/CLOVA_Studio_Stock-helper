import os
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import JWTError, jwt
from typing import Optional

from db.db import get_db_session
from db.models import AuthModels
from schemas import auth_schemas

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/signup", response_model=auth_schemas.User)
def create_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db_session)):
    db_user = (
        db.query(AuthModels.User).filter(AuthModels.User.email == user.email).first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = AuthModels.User(
        email=user.email, password=hashed_password, nickname=user.nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=auth_schemas.Token)
async def login_for_access_token(
    request: auth_schemas.UserLogin, db: Session = Depends(get_db_session)
):
    data = request.model_dump()
    email = data.get("email")
    password = data.get("password")
    if email is None or password is None:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = db.query(AuthModels.User).filter(AuthModels.User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        media_type="application/json",
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
        expires=int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
    )

    return response


def get_current_user(request: Request, db: Session = Depends(get_db_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    # Ensure token starts with "Bearer " and extract the actual token
    if token.startswith("Bearer "):
        token = token[len("Bearer ") :]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(AuthModels.User).filter(AuthModels.User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user


@router.get("/me", response_model=auth_schemas.User)
def read_users_me(current_user: auth_schemas.User = Depends(get_current_user)):
    return current_user


@router.delete("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}
