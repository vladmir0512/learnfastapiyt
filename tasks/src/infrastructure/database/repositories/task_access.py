from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models.task_access import TaskAccess


class TaskAccessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def grant(self, task_id: int, user_id: int):
        existing = await self.get(task_id, user_id)
        if not existing:
            self.session.add(TaskAccess(task_id=task_id, user_id=user_id))

    async def revoke(self, task_id: int, user_id: int):
        stmt = delete(TaskAccess).where(
            TaskAccess.task_id == task_id,
            TaskAccess.user_id == user_id
        )
        await self.session.execute(stmt)

    async def get(self, task_id: int, user_id: int):
        stmt = select(TaskAccess).where(
            TaskAccess.task_id == task_id,
            TaskAccess.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_task_ids_for_user(self, user_id: int):
        stmt = select(TaskAccess.task_id).where(TaskAccess.user_id == user_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_users_with_access(self, task_id: int):
        stmt = select(TaskAccess.user_id).where(TaskAccess.task_id == task_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]


def task_access_repository_factory(session):
    return TaskAccessRepository(session)
