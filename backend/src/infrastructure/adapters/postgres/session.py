from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    """Owns the async engine and hands out sessions."""

    def __init__(self, dsn: str, echo: bool = False) -> None:
        self._engine = create_async_engine(dsn, echo=echo, pool_pre_ping=True)
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def engine(self):
        return self._engine

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self) -> None:
        await self._engine.dispose()


_database: Database | None = None


def get_database(dsn: str | None = None) -> Database:
    global _database
    if _database is None:
        if dsn is None:
            raise RuntimeError("Database not initialized; provide a DSN on first call.")
        _database = Database(dsn)
    return _database
