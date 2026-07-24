from infrastructure.database.models.task import Task
from infrastructure.database.repositories.task import task_repository_factory
from infrastructure.database.repositories.task_access import task_access_repository_factory
from infrastructure.database.uow import unit_of_work
from core.exceptions import TaskNotFoundError


class TaskService:
    def __init__(self, repository_factory):
        self.task_repository_factory = repository_factory

    async def create(self, title, description, creator_id, assigned_to):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            task = Task(id=None, title=title, description=description, creator_id=creator_id, assigned_to=assigned_to)
            await repo.add(task)

    async def _get_shared_task_ids(self, user_id):
        async with unit_of_work() as uow:
            access_repo = task_access_repository_factory(uow.session)
            return await access_repo.get_task_ids_for_user(user_id)

    async def get(self, task_id, user_id):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            task = await repo.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.creator_id == user_id or user_id in (task.assigned_to or []):
                return task

            shared_ids = await self._get_shared_task_ids(user_id)
            if task_id in shared_ids:
                return task

            raise TaskNotFoundError(f"Task {task_id} not found")

    async def get_user_tasks(self, user_id):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            all_tasks = await repo.get_all()

            shared_ids = await self._get_shared_task_ids(user_id)

            return [
                t for t in all_tasks
                if t.creator_id == user_id
                or user_id in (t.assigned_to or [])
                or t.id in shared_ids
            ]

    async def get_all_tasks(self):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            return await repo.get_all()

    async def update(self, task_id, data, user_id):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            task = await repo.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")
            if task.creator_id != user_id:
                raise TaskNotFoundError(f"Task {task_id} not found")
            return await repo.update(task_id, data)

    async def delete(self, task_id, user_id):
        async with unit_of_work() as uow:
            repo = self.task_repository_factory(uow.session)
            task = await repo.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")
            if task.creator_id != user_id:
                raise TaskNotFoundError(f"Task {task_id} not found")
            return await repo.delete(task_id)

task_service = TaskService(task_repository_factory)