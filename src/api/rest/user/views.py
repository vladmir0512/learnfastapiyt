from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from jose import JWTError
from starlette import status

from api.rest.user.decorators import handle_user_errors
from core.permissions import Permissions
from core.user.services import user_service, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES, \
    TokenIsNotValidError
from dependencies import get_current_user

users_router = APIRouter(prefix="/users", tags=["Пользователи"])


@users_router.post("")
@handle_user_errors
def add_user(username: str, password: str, email:str, is_admin: bool, permissions: Optional[List[str]] = Query(
    default=None,
    title="Permissions",
    example=Permissions.list(),
    enum=Permissions.list()
)):

    user_service.add(username=username, password=password, email=email, is_admin=is_admin, permissions=permissions)
    return {"message": f"User {username} was added successfully"}

@users_router.get("")
def get_all_users():
    return user_service.get_all()

@users_router.get("/login")
def login(username: str, password: str):
    user = user_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = user_service.create_token(data={"sub": username, "type": "access"}, expires_delta=access_token_expires)
    refresh_token = user_service.create_token(data={"sub": username, "type": "refresh"}, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@users_router.post("/refresh")
def refresh_access_token(token: str):
    try:
        username = user_service.verify_token(token, "refresh")
    except (JWTError, TokenIsNotValidError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_token(
        data={"sub": username, "type": "access"},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token}




@users_router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}"}