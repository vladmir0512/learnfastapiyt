from datetime import timedelta, datetime
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from jose import jwt

SECRET_KEY = "super_secret"
ALGORITHM = "HS256"


def create_test_token(user_id: int = 1, email: str = "test@example.com") -> str:
    payload = {
        "sub": email,
        "user_id": user_id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.mark.asyncio
async def test_create_task(client):
    http, mock_uc = client
    token = create_test_token()
    response = await http.post(
        "/v1/api/tasks",
        json={"title": "Test Task", "description": "desc", "assigned_to": [1, 2]},
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Task 'Test Task' created successfully"


@pytest.mark.asyncio
async def test_create_task_unauthorized(client):
    http, mock_uc = client
    response = await http.post(
        "/v1/api/tasks",
        json={"title": "Test Task", "description": "desc", "assigned_to": [1]},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_my_tasks(client):
    http, mock_uc = client
    token = create_test_token()
    await http.post(
        "/v1/api/tasks",
        json={"title": "Task 1", "description": "desc", "assigned_to": []},
        headers={"Authorization": token},
    )
    response = await http.get(
        "/v1/api/tasks",
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_my_tasks_unauthorized(client):
    http, mock_uc = client
    response = await http.get("/v1/api/tasks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_task(client):
    http, mock_uc = client
    token = create_test_token()
    await http.post(
        "/v1/api/tasks",
        json={"title": "Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token},
    )

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Task"
    assert response.json()["creator_email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_task_no_access(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_stranger = create_test_token(user_id=99, email="stranger@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Private Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 99, "email": "stranger@example.com", "username": "stranger", "is_admin": False})

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token_stranger},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client):
    http, mock_uc = client
    token = create_test_token()
    await http.post(
        "/v1/api/tasks",
        json={"title": "To Delete", "description": "desc", "assigned_to": []},
        headers={"Authorization": token},
    )
    response = await http.delete(
        "/v1/api/tasks/1",
        headers={"Authorization": token},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_task_no_access(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_stranger = create_test_token(user_id=99, email="stranger@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Private Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 99, "email": "stranger@example.com", "username": "stranger", "is_admin": False})

    response = await http.delete(
        "/v1/api/tasks/1",
        headers={"Authorization": token_stranger},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(client):
    http, mock_uc = client
    token = create_test_token()
    await http.post(
        "/v1/api/tasks",
        json={"title": "Old Title", "description": "desc", "assigned_to": []},
        headers={"Authorization": token},
    )
    response = await http.patch(
        "/v1/api/tasks/1",
        json={"title": "New Title", "description": "new desc", "assigned_to": [2]},
        headers={"Authorization": token},
    )
    assert response.status_code == 200

    get_resp = await http.get("/v1/api/tasks/1", headers={"Authorization": token})
    assert get_resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_task_no_access(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_stranger = create_test_token(user_id=99, email="stranger@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Private Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 99, "email": "stranger@example.com", "username": "stranger", "is_admin": False})

    response = await http.patch(
        "/v1/api/tasks/1",
        json={"title": "Hacked", "description": "x", "assigned_to": []},
        headers={"Authorization": token_stranger},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_task_visible_to_assigned(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_assigned = create_test_token(user_id=42, email="assigned@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Shared Task", "description": "desc", "assigned_to": [42]},
        headers={"Authorization": token_owner},
    )

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 42, "email": "assigned@example.com", "username": "assigned", "is_admin": False})

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token_assigned},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Shared Task"


@pytest.mark.asyncio
async def test_share_task(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_shared = create_test_token(user_id=55, email="shared@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})
    mock_uc.get_user_by_email = AsyncMock(return_value={"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Shareable Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    response = await http.post(
        "/v1/api/tasks/1/share",
        json={"email": "shared@example.com"},
        headers={"Authorization": token_owner},
    )
    assert response.status_code == 200

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False})

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token_shared},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Shareable Task"


@pytest.mark.asyncio
async def test_unshare_task(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)
    token_shared = create_test_token(user_id=55, email="shared@example.com")

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})
    mock_uc.get_user_by_email = AsyncMock(return_value={"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Unshare Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    await http.post(
        "/v1/api/tasks/1/share",
        json={"email": "shared@example.com"},
        headers={"Authorization": token_owner},
    )

    response = await http.request(
        "DELETE",
        "/v1/api/tasks/1/share",
        content='{"email": "shared@example.com"}',
        headers={"Authorization": token_owner, "Content-Type": "application/json"},
    )
    assert response.status_code == 200

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False})

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token_shared},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_share_task_not_found(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)

    mock_uc.get_user_by_id = AsyncMock(return_value={"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False})
    mock_uc.get_user_by_email = AsyncMock(return_value=None)

    await http.post(
        "/v1/api/tasks",
        json={"title": "Task", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    response = await http.post(
        "/v1/api/tasks/1/share",
        json={"email": "nonexistent@example.com"},
        headers={"Authorization": token_owner},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_task_creator_sees_shared_with(client):
    http, mock_uc = client
    token_owner = create_test_token(user_id=1)

    def get_user_side_effect(uid):
        users = {
            1: {"id": 1, "email": "owner@example.com", "username": "owner", "is_admin": False},
            55: {"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False},
        }
        return users.get(uid)

    mock_uc.get_user_by_id = AsyncMock(side_effect=get_user_side_effect)
    mock_uc.get_user_by_email = AsyncMock(return_value={"id": 55, "email": "shared@example.com", "username": "shared", "is_admin": False})

    await http.post(
        "/v1/api/tasks",
        json={"title": "Task with shares", "description": "desc", "assigned_to": []},
        headers={"Authorization": token_owner},
    )

    await http.post(
        "/v1/api/tasks/1/share",
        json={"email": "shared@example.com"},
        headers={"Authorization": token_owner},
    )

    response = await http.get(
        "/v1/api/tasks/1",
        headers={"Authorization": token_owner},
    )
    assert response.status_code == 200
    assert "shared@example.com" in response.json()["shared_with"]
