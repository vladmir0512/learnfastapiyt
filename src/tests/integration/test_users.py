from datetime import timedelta
from http import HTTPStatus

import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.user.services import user_service, ACCESS_TOKEN_EXPIRE_MINUTES
from infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_user_register(client: AsyncClient, db_session: Session):
    response = await client.post("v1/api/users/register", json={
        "username": "test_user",
        "password": "secure-password",
        "email": "test@example.com",
    })
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User test_user added successfully'}

    stmt = select(User).where(User.email == "test@example.com")
    result = db_session.execute(stmt)
    user = result.scalars().first()

    assert user is not None


async def test_user_register_user_already_exists(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password="secure-password",
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()

    response = await client.post("v1/api/users/register", json={
        "username": "test_user",
        "password": "secure-password",
        "email": "test@example.com",
    })

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User already exists'}


async def test_user_login(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password=bcrypt.hashpw("secure-password".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()

    response = await client.post("v1/api/users/login", json={
        "password": "secure-password",
        "email": "test@example.com",
    })

    assert response.status_code == HTTPStatus.OK


async def test_user_login_failed(client: AsyncClient, db_session: Session):
    response = await client.post("v1/api/users/login", json={
        "password": "secure-password",
        "email": "test@example.com",
    })

    assert response.status_code == 401
    assert response.json() == {'detail': 'Incorrect username or password'}


async def test_get_users(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password="secure-password",
            username="test_user",
            is_admin=True
        )
    )
    db_session.commit()
    user = db_session.execute(select(User).where(User.email == "test@example.com")).scalars().first()
    access_token = await user_service.create_token(
        data={"sub": user.email, "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = await client.get("v1/api/users", headers={"Authorization": access_token})

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == "test@example.com"


async def test_get_users_permission_denied(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password="secure-password",
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()
    user = db_session.execute(select(User).where(User.email == "test@example.com")).scalars().first()
    access_token = await user_service.create_token(
        data={"sub": user.email, "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = await client.get("v1/api/users", headers={"Authorization": access_token})

    assert response.status_code == HTTPStatus.FORBIDDEN


async def test_get_me(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password="secure-password",
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()
    user = db_session.execute(select(User).where(User.email == "test@example.com")).scalars().first()
    access_token = await user_service.create_token(
        data={"sub": user.email, "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = await client.get("v1/api/users/me", headers={"Authorization": access_token})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['email'] == 'test@example.com'


async def test_get_me_auth_failed(client: AsyncClient, db_session: Session):
    response = await client.get("v1/api/users/me")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Authentication failed'}


async def test_patch_user(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="patch@example.com",
            password="secure-password",
            username="patch_user",
            is_admin=False
        )
    )
    db_session.add(
        User(
            email="admin@example.com",
            password="secure-password",
            username="admin",
            is_admin=True
        )
    )
    db_session.commit()
    admin = db_session.execute(select(User).where(User.email == "admin@example.com")).scalars().first()
    user = db_session.execute(select(User).where(User.email == "patch@example.com")).scalars().first()
    access_token = await user_service.create_token(
        data={"sub": admin.email, "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = await client.patch(
        f"v1/api/users/{user.id}", json={"is_admin": True}, headers={"Authorization": access_token}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"is_admin": True}
    db_session.refresh(user)
    assert user.is_admin is True


async def test_get_user_update_permission_denied(client: AsyncClient, db_session: Session):
    db_session.add(
        User(
            email="test@example.com",
            password="secure-password",
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()
    user = db_session.execute(select(User).where(User.email == "test@example.com")).scalars().first()
    access_token = await user_service.create_token(
        data={"sub": user.email, "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = await client.patch(f"v1/api/users/{user.id}", json={"is_admin": True}, headers={"Authorization": access_token})

    assert response.status_code == HTTPStatus.FORBIDDEN


async def test_get_user_update_auth_failed(client: AsyncClient, db_session: Session):
    response = await client.patch("v1/api/users/1", json={})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Authentication failed'}
