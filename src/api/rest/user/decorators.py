from functools import wraps
from inspect import signature
from typing import List

from fastapi import HTTPException
from starlette import status

from core.user.exceptions import TokenIsNotValidError, UserAlreadyExistsError


def check_permissions_decorator(required_permissions: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")


            if current_user is None:
                raise RuntimeError(
                    "Endpoint must have current_user parameter"
                )

            if not set(required_permissions).issubset(current_user.permissions):
                raise HTTPException(
                    status_code=403,
                    detail="User does not have necessary permissions",
                )

            return await func(*args, **kwargs)
        wrapper.__signature__ = signature(func)

        return wrapper
    return decorator


def handle_user_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (TokenIsNotValidError, UserAlreadyExistsError) as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=(error))

    return wrapper