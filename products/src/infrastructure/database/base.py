from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import  sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config import settings

engine = create_async_engine(settings.async_database_url, poolclass=NullPool)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session