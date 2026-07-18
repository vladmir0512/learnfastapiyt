from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError
from starlette import status

from users.services import UserService, TokenIsNotValidError


def get_current_user(token: str = Depends(APIKeyHeader(name="Authorization"))):
    try:
        return UserService.get_current_user(token)
    except (JWTError, TokenIsNotValidError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
