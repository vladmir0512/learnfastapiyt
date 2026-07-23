from datetime import datetime

import bcrypt
from jose import jwt

from core.user.entities import RegularUser
from core.user.exceptions import UserAlreadyExistsError, TokenIsNotValidError
from infrastructure.database.repositories.user import user_repository_factory
from infrastructure.database.uow import unit_of_work

ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 10
SECRET_KEY = "super_secret"
ALGORITHM = "HS256"


class UserService:

    def __init__(self, repository_factory):
        self.user_repository_factory = repository_factory

    async def create(self, username, password, email):
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = RegularUser(username=username, password=hashed_password, email=email)
        async with unit_of_work() as uow:
            user_repository = self.user_repository_factory(uow.session)
            existing_user = await user_repository.get_by_email(email)
            if existing_user:
                raise UserAlreadyExistsError("User already exists")

            await user_repository.add(user)

    async def get_all(self):
        async with unit_of_work() as uow:
            user_repository = self.user_repository_factory(uow.session)
            return await user_repository.get_all()

    async def patch(self, user_id, user):
        async with unit_of_work() as uow:
            user_repository = self.user_repository_factory(uow.session)
            return await user_repository.update(user_id, user)

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    async def authenticate_user(self, email, password):
        async with unit_of_work() as uow:
            user_repository = self.user_repository_factory(uow.session)
            user = await user_repository.get_by_email(email)
        if not user or not self.verify_password(password, user.password):
            return None
        return user

    @staticmethod
    async def create_token(data, expires_delta):
        payload = data.copy()
        expire = datetime.utcnow() + expires_delta
        payload.update({"exp": expire})
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(self, token):
        async with unit_of_work() as uow:
            user_repository = self.user_repository_factory(uow.session)
            email = self.verify_token(token, "access")
            return await user_repository.get_by_email(email)

    @staticmethod
    def verify_token(token, token_type):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        current_token_type = payload.get("type")
        if current_token_type != token_type:
            raise TokenIsNotValidError("Token is not valid")
        return payload.get("sub")


user_service = UserService(user_repository_factory)
