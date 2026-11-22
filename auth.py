import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError

from database import get_user, get_user_by_id, register_user, update_user

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
if not SECRET_KEY or ALGORITHM != "HS256":
    raise ValueError("Set SECRET_KEY and ALGORITHM=HS256 in your .env")

pw_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")
router = APIRouter(prefix="/auth/users", tags=["Authentication"])


def hash_password(password: str) -> str:
    return pw_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pw_hash.verify(password, hashed_password)


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})


def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found",
                            headers={"WWW-Authenticate": "Bearer"})
    return user


class UserRegister(BaseModel):
    username: EmailStr
    phone: str = Field(min_length=5)
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)
    city: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: int
    username: EmailStr
    phone: str
    name: str
    city: str


class UserUpdate(BaseModel):
    phone: str | None = Field(default=None, min_length=5)
    name: str | None = Field(default=None, min_length=1)
    city: str | None = Field(default=None, min_length=1)


def user_response(user):
    return {
        "id": user.user_id,
        "username": user.username,
        "phone": user.phone,
        "name": user.name,
        "city": user.city
    }


@router.post("/", response_model=UserResponse, status_code=200)
def register(user: UserRegister):
    try:
        user_id = register_user(
            username=user.username,
            phone=user.phone,
            hashed_password=hash_password(user.password),
            name=user.name,
            city=user.city
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")
    return user_response(get_user_by_id(user_id))

@router.post("/login", status_code=200)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_token(user.user_id), "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, status_code=200)
def me(user=Depends(get_current_user)):
    return user_response(user)
@router.patch("/me", response_model=UserResponse, status_code=200)
def update_me(data: UserUpdate, user=Depends(get_current_user)):
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided")

    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Fields cannot be null")

    updated_user = update_user(user.user_id, changes)
    return user_response(updated_user)

