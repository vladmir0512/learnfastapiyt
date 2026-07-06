from datetime import datetime
from os import access

from anyio.lowlevel import current_token
from fastapi import HTTPException

import bcrypt
from click import pause
from fastapi.params import Depends
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from starlette import status

from users.managers import user_manager


SECRET_KEY = "super_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 10

class UserService:

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        print(f"Hash type: {type(hashed_password)}, value: {hashed_password!r}")  # <-- debug
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    @classmethod
    def authenticate_user(cls, username, password):
        user = user_manager.users.get(username)
        if not user or not cls.verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def create_token(data, expires_delta):
        payload = data.copy()
        expire = datetime.now() + expires_delta
        payload.update({"exp": expire})
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def get_current_user(cls, token= Depends(APIKeyHeader(name="Authorization"))):
        username = cls.verify_token(token, "access")
        return user_manager.users.get(username)


    @staticmethod
    def verify_token(token, token_type):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")
            current_token_type = payload.get("type")
            if current_token_type != token_type or datetime.fromtimestamp(exp) < datetime.now():
                raise HTTPException(status_code=401, detail="Token is not valid")
            return payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication error"
            )
