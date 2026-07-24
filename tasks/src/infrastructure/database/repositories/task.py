from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models.task import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task):
        self.session.add(Task(
            title=task.title, description=task.description,
            creator_id=task.creator_id, assigned_to=task.assigned_to
        ))

    async def get_by_id(self, task_id):
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalars().first()

    async def get_all(self):
        result = await self.session.execute(select(Task))
        return result.scalars().all()

    async def update(self, task_id, data):
        stmt = update(Task).where(Task.id == task_id).values(**data)
        await self.session.execute(stmt)

    async def delete(self, task_id):
        stmt = delete(Task).where(Task.id == task_id)
        await self.session.execute(stmt)

def task_repository_factory(session):
    return TaskRepository(session)