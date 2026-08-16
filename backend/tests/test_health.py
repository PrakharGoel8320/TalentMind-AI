import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_health_check_healthy(async_client, mocker):
    # Mock dependencies directly in FastAPI dependency overrides
    from app.main import app
    from app.database.session import get_db
    from app.database.redis import get_redis
    from app.database.neo4j_client import get_neo4j
    
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_neo4j = AsyncMock()
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_neo4j] = lambda: mock_neo4j
    
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dependencies"]["postgres"] == "healthy"
    assert data["dependencies"]["redis"] == "healthy"
    assert data["dependencies"]["neo4j"] == "healthy"
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check_degraded(async_client, mocker):
    from app.main import app
    from app.database.session import get_db
    from app.database.redis import get_redis
    from app.database.neo4j_client import get_neo4j
    
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB Down")
    
    mock_redis = AsyncMock()
    mock_neo4j = AsyncMock()
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_neo4j] = lambda: mock_neo4j
    
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["dependencies"]["postgres"] == "unhealthy"
    assert data["dependencies"]["redis"] == "healthy"
    
    app.dependency_overrides.clear()
