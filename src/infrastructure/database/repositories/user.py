from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.user.entities import BaseUser
from infrastructure.database.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def update(self, user_id, user):
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_admin=user.is_admin)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)

    async def add(self, user: BaseUser):
        self.session.add(
            User(
                email=user.email,
                password=user.password,
                username=user.username,
                is_admin=user.is_admin,
            )
        )


def user_repository_factory(session):
    return UserRepository(session)