from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError
from starlette import status

from core.user.services import TokenIsNotValidError, user_service


async def get_current_user(token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False))):
    try:
        return await user_service.get_current_user(token)
    except (JWTError, TokenIsNotValidError, AttributeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")


def context_dependency(current_user: str = Depends(get_current_user)):
    return {"current_user": current_user}
