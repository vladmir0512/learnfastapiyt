import logging
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError
from starlette import status

from api.rest.decorators import handle_user_errors, check_permissions_decorator
from api.rest.models import UserCreate, UserLogin, PatchUser, CurrentUser
from dependencies import get_current_user, verify_internal_key
from core.exceptions import UserAlreadyExistsError, ServiceError
from core.services import user_service, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, \
    TokenIsNotValidError

logger = logging.getLogger("fastapi-app")

users_router = APIRouter(prefix="/users", tags=["Пользователи"])


@users_router.post("/register")
@handle_user_errors
async def register(user: UserCreate):
    try:
        await user_service.create(username=user.username, password=user.password, email=user.email)
    except UserAlreadyExistsError as e:
        logger.warning("Registration failed. Email: %s - %s", user.email, e)
        raise
    except ServiceError as e:
        logger.error("Registration error. Username: %s - %s", user.username, e)
        raise
    logger.info("User successfully registered. Username: %s", user.username)
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
        logger.warning("Failed login attempt for email: %s", user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    logger.info("User successfully authorized. User email: %s", authenticated_user.email)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = await user_service.create_token(
        data={"sub": authenticated_user.email, "user_id": authenticated_user.id, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token = await user_service.create_token(
        data={"sub": authenticated_user.email, "user_id": authenticated_user.id, "type": "refresh"}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@users_router.post("/refresh")
async def refresh_access_token(token: str):
    try:
        payload = user_service.verify_token_payload(token, "refresh")
        email = payload.get("sub")
        user_id = payload.get("user_id")
    except (JWTError, TokenIsNotValidError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await user_service.create_token(
        data={"sub": email, "user_id": user_id, "type": "access"},
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


@users_router.get("/{user_id}")
async def get_user_by_id(user_id: int, _key: str = Depends(verify_internal_key)):
    from infrastructure.database.repositories.user import user_repository_factory
    from infrastructure.database.uow import unit_of_work
    async with unit_of_work() as uow:
        repo = user_repository_factory(uow.session)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "email": user.email, "username": user.username, "is_admin": user.is_admin}


@users_router.get("/by-email/{email}")
async def get_user_by_email(email: str, _key: str = Depends(verify_internal_key)):
    from infrastructure.database.repositories.user import user_repository_factory
    from infrastructure.database.uow import unit_of_work
    async with unit_of_work() as uow:
        repo = user_repository_factory(uow.session)
        user = await repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "email": user.email, "username": user.username, "is_admin": user.is_admin}
