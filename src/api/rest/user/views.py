from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError
from starlette import status

from api.rest.user.decorators import handle_user_errors, check_permissions_decorator
from api.rest.user.models import UserCreate, UserLogin, PatchUser, CurrentUser
from dependencies import get_current_user
from core.user.services import user_service, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, \
    TokenIsNotValidError

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post("/register")
@handle_user_errors
async def register(user: UserCreate):
    await user_service.create(username=user.username, password=user.password, email=user.email)
    return {"message": f"User {user.username} added successfully"}


@users_router.get("")
@check_permissions_decorator([])
async def get_all_user(current_user=Depends(get_current_user)):
    users = await user_service.get_all()
    return [CurrentUser.model_validate(u) for u in users]


@users_router.post("/login")
async def login(user: UserLogin):
    authenticated_user = await user_service.authenticate_user(user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = await user_service.create_token(
        data={"sub": authenticated_user.email, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token = await user_service.create_token(
        data={"sub": authenticated_user.email, "type": "refresh"}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@users_router.post("/refresh")
async def refresh_access_token(token: str):
    try:
        email = user_service.verify_token(token, "refresh")
    except (JWTError, TokenIsNotValidError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await user_service.create_token(
        data={"sub": email, "type": "access"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token}


@users_router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return CurrentUser.model_validate(current_user)


@users_router.patch("/{user_id}")
@check_permissions_decorator([])
async def patch_user(user_id: int, user: PatchUser, current_user=Depends(get_current_user)):
    await user_service.patch(user_id, user)
    return {"is_admin": user.is_admin}
