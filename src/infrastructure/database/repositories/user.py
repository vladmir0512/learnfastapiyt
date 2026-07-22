from poetry.utils import password_manager
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.user.entities import BaseUser
from infrastructure.database.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_username(self, username: str):
        stnt = select(User).where(User.username == username)
        result = await self.session.execute(stnt)
        return result.scalars().first()

    async def get_all(self):
        return self.session.query(User).all()

    async def add(self, user: BaseUser):
        self.session.add(
                User(
                    email=user.email,
                    password=user.password,
                    username=user.username,
                    is_admin=user.is_admin
            )
        )


def user_repository_factory(session):
    return UserRepository(session)