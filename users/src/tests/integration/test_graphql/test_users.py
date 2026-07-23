import bcrypt
import pytest

from infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_register(client):
    query = """
    mutation {
        register(username: "Admin", password: "securepass", email: "admin@example.com") {
            username
            email
        }
    }
    """
    response = await client.post("/v1/graphql", json={"query": query})

    data = response.json()

    assert response.status_code == 200
    assert "data" in data
    assert data["data"]["register"]["username"] == "Admin"
    assert data["data"]["register"]["email"] == "admin@example.com"


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    db_session.add(
        User(
            email="admin@example.com",
            password=bcrypt.hashpw("securepass".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            username="test_user",
            is_admin=False
        )
    )
    db_session.commit()

    query = """
    mutation {
        login(email: "admin@example.com", password: "securepass") {
            accessToken
            refreshToken
        }
    }
    """
    response = await client.post("/v1/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "accessToken" in data["data"]["login"]
    assert "refreshToken" in data["data"]["login"]


@pytest.mark.asyncio
async def test_login_fail(client):
    query = """
    mutation {
        login(email: "admin@example.com", password: "wrongpass") {
            accessToken
            refreshToken
        }
    }
    """
    response = await client.post("/v1/graphql", json={"query": query})
    data = response.json()
    assert response.status_code == 200
    assert "errors" in data
    assert "Incorrect username or password" in data["errors"][0]["message"]
