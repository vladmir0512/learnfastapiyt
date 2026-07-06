from datetime import timedelta
from typing import List, Optional

import bcrypt
from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from jose import JWTError
from starlette import status

from users.dependencies import get_current_user
from users.models import PERMISSIONS
from users.services import UserService, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, TokenIsNotValidError

users_router = APIRouter(prefix="/users", tags=["Пользователи"])


@users_router.post("")
def add_user(username: str, password: str, email:str, is_admin: bool, permissions: Optional[List[str]] = Query(
    default=None,
    title="Permissions",
    example=PERMISSIONS,
    enum=PERMISSIONS
)):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    UserService.add(username=username, password=hashed_password, email=email, is_admin=is_admin, permissions=permissions)
    return {"message": f"User {username} was added successfully"}

@users_router.get("")
def get_all_users():
    return UserService.get_all()

@users_router.get("/login")
def login(username: str, password: str):
    user = UserService.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = UserService.create_token(data={"sub": username, "type": "access"}, expires_delta=access_token_expires)
    refresh_token = UserService.create_token(data={"sub": username, "type": "refresh"}, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@users_router.post("/refresh")
def refresh_access_token(token: str):
    try:
        username = UserService.verify_token(token, "refresh")
    except (JWTError, TokenIsNotValidError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = UserService.create_token(
        data={"sub": username, "type": "access"},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token}




@users_router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}"}