from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncConnection, AsyncSession

from config import DB_URL, DB_ECHO


class DatabaseSessionManager:
    def __init__(self, db_url: str, **engine_kwargs):
        self._engine = create_async_engine(db_url, **engine_kwargs)
        self._async_session = async_sessionmaker(bind=self._engine, autocommit=False)

    async def close(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._async_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


db_session_manager = DatabaseSessionManager(DB_URL, echo=DB_ECHO)
