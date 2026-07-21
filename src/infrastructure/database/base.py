from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import  sessionmaker, declarative_base
from config import settings

engine = create_async_engine(settings.async_database_url)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

def get_db():
    db = async_session
    try:
        yield db
    finally:
        db.close()
