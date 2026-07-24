import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.services import task_service
from api.rest.decorators import handle_task_errors
from dependencies import get_current_user
from infrastructure.users_client import users_client
from infrastructure.database.uow import unit_of_work
from infrastructure.database.repositories.task_access import task_access_repository_factory

logger = logging.getLogger("fastapi-app")

tasks_router = APIRouter(prefix="/tasks", tags=["Задачи"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assigned_to: list[int] = []


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assigned_to: list[int] | None = None


class ShareTask(BaseModel):
    email: str


@tasks_router.post("")
@handle_task_errors
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    await task_service.create(
        title=task.title,
        description=task.description,
        creator_id=current_user["user_id"],
        assigned_to=task.assigned_to,
    )
    logger.info("Task created: '%s' by user_id=%d", task.title, current_user["user_id"])
    return {"message": f"Task '{task.title}' created successfully"}


def task_to_dict(task, creator_email=None, shared_with=None):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "creator_id": task.creator_id,
        "creator_email": creator_email or str(task.creator_id),
        "assigned_to": task.assigned_to,
        "shared_with": shared_with or [],
        "created_at": str(task.created_at) if task.created_at else None,
        "updated_at": str(task.updated_at) if task.updated_at else None,
    }


async def is_admin(user_id: int) -> bool:
    user = await users_client.get_user_by_id(user_id)
    return user.get("is_admin", False) if user else False


@tasks_router.get("")
@handle_task_errors
async def get_my_tasks(current_user=Depends(get_current_user)):
    user_id = current_user["user_id"]
    admin = await is_admin(user_id)

    if admin:
        tasks = await task_service.get_all_tasks()
    else:
        tasks = await task_service.get_user_tasks(user_id)

    result = []
    for t in tasks:
        creator = await users_client.get_user_by_id(t.creator_id)
        creator_email = creator["email"] if creator else str(t.creator_id)

        async with unit_of_work() as uow:
            access_repo = task_access_repository_factory(uow.session)
            shared_user_ids = await access_repo.get_users_with_access(t.id)

        shared_emails = []
        for uid in shared_user_ids:
            u = await users_client.get_user_by_id(uid)
            shared_emails.append(u["email"] if u else str(uid))

        result.append(task_to_dict(t, creator_email=creator_email, shared_with=shared_emails))
    return result


@tasks_router.get("/{task_id}")
@handle_task_errors
async def get_task(task_id: int, current_user=Depends(get_current_user)):
    task = await task_service.get(task_id, current_user["user_id"])
    creator = await users_client.get_user_by_id(task.creator_id)
    creator_email = creator["email"] if creator else str(task.creator_id)

    async with unit_of_work() as uow:
        access_repo = task_access_repository_factory(uow.session)
        shared_user_ids = await access_repo.get_users_with_access(task.id)

    shared_emails = []
    for uid in shared_user_ids:
        u = await users_client.get_user_by_id(uid)
        shared_emails.append(u["email"] if u else str(uid))

    return task_to_dict(task, creator_email=creator_email, shared_with=shared_emails)


@tasks_router.post("/{task_id}/share")
@handle_task_errors
async def share_task(task_id: int, body: ShareTask, current_user=Depends(get_current_user)):
    task = await task_service.get(task_id, current_user["user_id"])

    target_user = await users_client.get_user_by_email(body.email)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    async with unit_of_work() as uow:
        access_repo = task_access_repository_factory(uow.session)
        await access_repo.grant(task_id, target_user["id"])

    logger.info("Task %d shared with %s by user_id=%d", task_id, body.email, current_user["user_id"])
    return {"message": f"Task shared with {body.email}"}


@tasks_router.delete("/{task_id}/share")
@handle_task_errors
async def unshare_task(task_id: int, body: ShareTask, current_user=Depends(get_current_user)):
    task = await task_service.get(task_id, current_user["user_id"])

    target_user = await users_client.get_user_by_email(body.email)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    async with unit_of_work() as uow:
        access_repo = task_access_repository_factory(uow.session)
        await access_repo.revoke(task_id, target_user["id"])

    logger.info("Task %d unshared from %s by user_id=%d", task_id, body.email, current_user["user_id"])
    return {"message": f"Access revoked for {body.email}"}


@tasks_router.patch("/{task_id}")
@handle_task_errors
async def update_task(task_id: int, task: TaskUpdate, current_user=Depends(get_current_user)):
    data = {k: v for k, v in task.model_dump().items() if v is not None}
    await task_service.update(task_id, data, current_user["user_id"])
    logger.info("Task %d updated by user_id=%d: %s", task_id, current_user["user_id"], data)
    return {"message": f"Task {task_id} updated successfully"}


@tasks_router.delete("/{task_id}")
@handle_task_errors
async def delete_task(task_id: int, current_user=Depends(get_current_user)):
    await task_service.delete(task_id, current_user["user_id"])
    logger.info("Task %d deleted by user_id=%d", task_id, current_user["user_id"])
    return {"message": f"Task {task_id} deleted successfully"}
