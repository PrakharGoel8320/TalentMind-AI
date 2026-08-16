import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.models.action import ActionProposal
from app.models.enums import ActionStatus, ActionType
from app.services.action_executor import assert_action_approved
from app.core.exceptions import ForbiddenError, NotFoundError
from app.database.session import get_db
from app.core.auth import get_current_user, UserContext
from datetime import datetime

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
async def test_list_proposals(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, target_id="cand_1", status=ActionStatus.PENDING_APPROVAL)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.get("/api/v1/approvals/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "12345678-1234-5678-1234-567812345678"
    assert data[0]["action_type"] == "EMAIL_CANDIDATE"

@pytest.mark.asyncio
async def test_approve_proposal(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, target_id="cand_1", status=ActionStatus.PENDING_APPROVAL)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_reject_proposal(async_client, mock_db):
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, target_id="cand_1", status=ActionStatus.PENDING_APPROVAL)
    mock_db.execute.return_value = create_mock_result(proposal)
    
    response = await async_client.post("/api/v1/approvals/12345678-1234-5678-1234-567812345678/reject")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_security_boundary_approved():
    db = AsyncMock()
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, target_id="cand_1", status=ActionStatus.APPROVED)
    db.execute.return_value = create_mock_result(proposal)
    
    # Should not raise exception
    returned_action = await assert_action_approved(db, "12345678-1234-5678-1234-567812345678")
    assert returned_action.id == "12345678-1234-5678-1234-567812345678"

@pytest.mark.asyncio
async def test_security_boundary_pending():
    db = AsyncMock()
    proposal = ActionProposal(id="12345678-1234-5678-1234-567812345678", action_type=ActionType.EMAIL_CANDIDATE, target_id="cand_1", status=ActionStatus.PENDING_APPROVAL)
    db.execute.return_value = create_mock_result(proposal)
    
    with pytest.raises(ForbiddenError) as exc_info:
        await assert_action_approved(db, "12345678-1234-5678-1234-567812345678")
    
    assert exc_info.value.status_code == 403
    assert "pending approval" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_agent_propose_action_tool(mocker):
    from app.ai.agent.tools import propose_action_tool
    
    # Mock the AsyncSessionLocal and its add/commit methods
    mock_session = AsyncMock()
    mocker.patch("app.database.session.AsyncSessionLocal", return_value=mock_session)
    mock_session.__aenter__.return_value = mock_session
    
    # Simulate a tool call from the agent
    result = propose_action_tool.invoke({
        "action_type": "EMAIL_CANDIDATE",
        "target_id": "cand_agent_test",
        "reason": "Because they are a good fit",
        "payload": {"body": "Hello"}
    })
    
    assert "PENDING_APPROVAL" in result
    assert "EMAIL_CANDIDATE" in result
    assert mock_session.add.called
    assert mock_session.commit.called
