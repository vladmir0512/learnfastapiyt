import pytest_asyncio
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from infrastructure.database.base import Base
from main import app

engine = create_engine(settings.sync_database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


MOCK_USER = {"id": 1, "email": "test@example.com", "username": "testuser", "is_admin": False}


@pytest_asyncio.fixture
async def client():
    with patch("api.rest.views.users_client") as mock_uc:
        mock_uc.get_user_by_id = AsyncMock(return_value=MOCK_USER)
        mock_uc.get_user_by_email = AsyncMock(return_value=MOCK_USER)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac, mock_uc
