from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DatabaseConfig, DatabaseType
from logging_config import logger
from typing import AsyncGenerator

connection_string = DatabaseConfig.get_connection_string(DatabaseType.USER)
engine = create_async_engine(connection_string, pool_size=10, max_overflow=0)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
        finally:
            await session.close()


