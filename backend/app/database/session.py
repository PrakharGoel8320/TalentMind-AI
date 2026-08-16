from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

db_url = settings.DATABASE_URL
if db_url.startswith('sqlite'):
    engine = create_async_engine(db_url, echo=False)
else:
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
