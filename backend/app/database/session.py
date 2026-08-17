import ssl
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings


def _normalize_db_url(url: str):
    """Return an (async-driver URL, connect_args) pair.

    Managed Postgres providers (Render, Heroku, Supabase, ...) hand out a
    synchronous ``postgres://`` / ``postgresql://`` URL. SQLAlchemy's async
    engine requires an async driver, so we rewrite the scheme to asyncpg.

    We also strip the libpq-style ``sslmode`` / ``channel_binding`` query
    parameters, which asyncpg does not understand (it would raise
    ``TypeError: connect() got an unexpected keyword argument 'sslmode'``),
    and translate ``sslmode`` into an asyncpg-compatible ``ssl`` connect arg.
    """
    connect_args: dict = {}
    url = (url or "").strip()

    # SQLite (local/dev) needs no rewriting.
    if url.startswith("sqlite"):
        return url, connect_args

    # Normalize the driver to asyncpg if a bare Postgres scheme was provided.
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    # Only massage query params for postgres/asyncpg URLs.
    if "asyncpg" in url:
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        sslmode = query.pop("sslmode", None)
        query.pop("channel_binding", None)  # libpq-only, unknown to asyncpg

        if sslmode and sslmode != "disable":
            if sslmode in ("verify-ca", "verify-full"):
                # Encrypt and verify the server certificate.
                connect_args["ssl"] = ssl.create_default_context()
            else:
                # `require` / `prefer` / `allow`: encrypt but do not verify,
                # matching libpq semantics and avoiding cert-chain failures.
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                connect_args["ssl"] = ctx

        url = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )

    return url, connect_args


db_url, connect_args = _normalize_db_url(settings.DATABASE_URL)

if db_url.startswith("sqlite"):
    engine = create_async_engine(db_url, echo=False)
else:
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        connect_args=connect_args,
    )

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
