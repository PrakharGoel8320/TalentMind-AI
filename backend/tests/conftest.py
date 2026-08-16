"""Shared pytest fixtures for TalentMind backend tests."""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.database.session import get_db
from app.core.auth import get_current_user, UserContext


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_user():
    return UserContext(
        user_id="00000000-0000-0000-0000-000000000001",
        role="RECRUITER",
    )


@pytest.fixture
async def async_client(mock_db, mock_user):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


def create_mock_result(proposal):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    if proposal:
        now = datetime.now(timezone.utc)
        if not getattr(proposal, "created_at", None):
            proposal.created_at = now
        if not getattr(proposal, "updated_at", None):
            proposal.updated_at = now
        mock_scalars.all.return_value = [proposal]
        mock_scalars.first.return_value = proposal
    else:
        mock_scalars.all.return_value = []
        mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    return mock_result
