import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / "core" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")

# psycopg2 URL → asyncpg URL for async engine
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgresql+psycopg2://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
