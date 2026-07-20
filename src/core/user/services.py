from datetime import datetime

import bcrypt
from jose import jwt

from core.user.entities import AdminUser, RegularUser
from users.managers import user_manager

SECRET_KEY = "super_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 10


class TokenIsNotValidError(Exception):
    pass


class UserService:

    @staticmethod
    def add(username, password, email, is_admin, permissions):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        if is_admin:
            user = AdminUser(username, hashed_password, email)
        else:
            user = RegularUser(username, hashed_password, email, permissions)

        user_manager.add_user(user)

    @staticmethod
    def get_all():
        return user_manager.get_all_users()

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
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
    def get_current_user(cls, token):
        username = cls.verify_token(token, "access")
        return user_manager.users.get(username)


    @staticmethod
    def verify_token(token, token_type):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        current_token_type = payload.get("type")
        if current_token_type != token_type:
            raise TokenIsNotValidError("Token is not valid")
        return payload.get("sub")

