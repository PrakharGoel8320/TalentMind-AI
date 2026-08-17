import os
# Performance Optimization: Constrain CPU threads to prevent context switching overhead during ML inference
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middlewares import CorrelationIdMiddleware, RequestLoggingMiddleware
from app.core.exceptions import DomainException, domain_exception_handler, generic_exception_handler
from app.utils.logger import setup_logger, get_logger
from app.api.v1 import health, candidates, jobs, skills, auth, agent, approvals
from app.database.session import engine
from app.models import Base
from app.database.neo4j_client import neo4j_client
from app.database.redis import close_redis

from contextlib import asynccontextmanager

setup_logger()
logger = get_logger("app.startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", version=settings.VERSION)
    
    # Automatically initialize database schema if tables do not exist
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_initialized")
    except Exception as e:
        logger.warning(f"database_table_init_notice: {e}")
    
    yield
    logger.info("app_shutting_down")
    await neo4j_client.close()
    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Exception Handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middlewares
from app.core.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins() if settings.cors_origins() else ["*"],
    allow_origin_regex=r"^https://.*\.vercel\.app$|^http://localhost(:\d+)?$|^http://127\.0\.0\.1(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix=f"{settings.API_V1_STR}", tags=["health"])
app.include_router(candidates.router, prefix=f"{settings.API_V1_STR}")
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}")
app.include_router(skills.router, prefix=f"{settings.API_V1_STR}")
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}")
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}")
app.include_router(approvals.router, prefix=f"{settings.API_V1_STR}/approvals", tags=["approvals"])
