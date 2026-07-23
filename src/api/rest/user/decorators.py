from functools import wraps
from typing import List

from fastapi import Depends, HTTPException
from starlette import status

from core.user.exceptions import UserAlreadyExistsError, TokenIsNotValidError, ServiceError
from dependencies import get_current_user


def check_permissions_decorator(required_permissions: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            if current_user.is_admin:
                return await func(*args, current_user=current_user, **kwargs)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="user does not have necessary permissions"
            )
        return wrapper
    return decorator


def handle_user_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (TokenIsNotValidError, UserAlreadyExistsError, ServiceError) as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return wrapper
