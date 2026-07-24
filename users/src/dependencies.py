import os
from fastapi import Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
from jose import JWTError
from starlette import status

from core.services import TokenIsNotValidError, user_service

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


async def get_current_user(token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False))):
    try:
        return await user_service.get_current_user(token)
    except (JWTError, TokenIsNotValidError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")


async def context_dependency(token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False))):
    try:
        current_user = await user_service.get_current_user(token)
        return {"current_user": current_user}
    except (JWTError, TokenIsNotValidError, AttributeError):
        return {"current_user": None}


async def verify_internal_key(x_internal_key: str = Header(None)):
    if not x_internal_key or x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid internal key")
