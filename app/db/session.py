import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,        # Confirms the connection is live before sending a query
    pool_recycle=300,          # Refreshes connection before Neon drops it for idling
    connect_args={"timeout": 60},
)
logger.info("Database engine created")

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_models():
    # Creates tables directly from models — no migration tool needed yet.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)