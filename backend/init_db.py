import asyncio
from app.database.session import engine
from app.core.base_class import Base
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.action import ActionProposal

async def init_db():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(init_db())
