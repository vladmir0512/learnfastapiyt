from typing import List

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

def check_permissions(required_permissions: List[str]):
    def permission_dependency(current_user=Depends(get_current_user)):
        user_permissions = current_user.permissions
        if not set(required_permissions).issubset(set(user_permissions)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not have necessary permissions")
        return current_user

    return permission_dependency