from functools import wraps
from typing import List

from fastapi import Depends, HTTPException
from starlette import status

from core.exceptions import TaskNotFoundError, TaskAlreadyExistsError
from dependencies import get_current_user


def check_permissions_decorator(required_permissions: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def handle_task_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TaskNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
        except TaskAlreadyExistsError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return wrapper