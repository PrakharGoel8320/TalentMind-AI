import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.models.action import ActionProposal
from app.models.enums import ActionStatus, ActionType
from app.database.session import get_db
from app.core.auth import get_current_user, UserContext

@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db

@pytest.fixture
async def async_client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: UserContext(
        user_id="00000000-0000-0000-0000-000000000001",
        role="RECRUITER",
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

def create_mock_result(proposal):
    from datetime import datetime
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    if proposal:
        if not getattr(proposal, "created_at", None):
            proposal.created_at = datetime.utcnow()
        if not getattr(proposal, "updated_at", None):
            proposal.updated_at = datetime.utcnow()
        mock_scalars.all.return_value = [proposal]
        mock_scalars.first.return_value = proposal
    else:
        mock_scalars.all.return_value = []
        mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars
    return mock_result

@pytest.mark.asyncio
async def test_execute_approved_succeeds_with_mock(async_client, mock_db):
    proposal = ActionProposal(
        id="12345678-1234-5678-1234-567812345678", 
        action_type=ActionType.EMAIL_CANDIDATE, 
        target_id="cand_1", 
        status=ActionStatus.APPROVED,
        payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello there"}
    )
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "EXECUTED"
    assert data["execution_result"] is not None
    assert data["execution_result"]["provider"] == "mock"
    assert data["provider"] == "mock"
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_execute_pending_fails(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.PENDING_APPROVAL)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 403
    assert "pending approval" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_execute_rejected_fails(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.REJECTED)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 403
    assert "rejected" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_duplicate_execution_fails(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.EXECUTED)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 403
    assert "already been executed" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_email_validation_missing_fields(async_client, mock_db):
    proposal = ActionProposal(
        id="12345678-1234-5678-1234-567812345678", 
        action_type=ActionType.EMAIL_CANDIDATE, 
        status=ActionStatus.APPROVED,
        payload={"subject": "Hi"} # Missing recipient and body
    )
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 400
    assert "recipient" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_execute_approved_by_other_user_fails(async_client, mock_db):
    proposal = ActionProposal(
        id="12345678-1234-5678-1234-567812345678",
        action_type=ActionType.EMAIL_CANDIDATE,
        status=ActionStatus.APPROVED,
        approved_by="00000000-0000-0000-0000-000000000099",
        payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello there"},
    )
    mock_db.execute.return_value = create_mock_result(proposal)

    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/execute")
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()
