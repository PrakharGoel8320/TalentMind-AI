"""
End-to-end workflow test covering the core TalentMind recruiter pipeline:
ranking -> agent proposal -> approval -> execution (mock email).

Uses mocked database sessions to keep the test fast and isolated while exercising
real service logic for approval guards and email dispatch.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.models.action import ActionProposal
from app.models.enums import ActionStatus, ActionType
from app.services.action_executor import assert_action_approved, execute_action
from app.ai.agent.tools import propose_action_tool
from tests.conftest import create_mock_result


@pytest.mark.asyncio
async def test_unapproved_action_cannot_execute():
    db = AsyncMock()
    proposal = ActionProposal(
        id="aaaaaaaa-1111-2222-3333-444444444444",
        action_type=ActionType.EMAIL_CANDIDATE,
        status=ActionStatus.PENDING_APPROVAL,
        payload={"recipient": "cand@example.com", "subject": "Hi", "body": "Hello"},
    )
    db.execute.return_value = create_mock_result(proposal)

    with pytest.raises(Exception) as exc:
        await assert_action_approved(db, "aaaaaaaa-1111-2222-3333-444444444444")
    assert "pending" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_full_recruiter_workflow_approve_then_execute(mock_db):
    """
    Simulates: agent proposes -> human approves -> execute -> EXECUTED with mock provider.
    """
    proposal = ActionProposal(
        id="bbbbbbbb-1111-2222-3333-444444444444",
        action_type=ActionType.EMAIL_CANDIDATE,
        target_id="candidate-123",
        reason="Strong fit for backend role",
        status=ActionStatus.PENDING_APPROVAL,
        payload={
            "recipient": "candidate@example.com",
            "subject": "Interview invitation",
            "body": "We would like to schedule an interview.",
        },
    )
    mock_db.execute.return_value = create_mock_result(proposal)

    # Step 1: Agent creates proposal (PENDING_APPROVAL)
    with patch("app.ai.agent.tools.AsyncSessionLocal") as mock_session_factory:
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        result = propose_action_tool.invoke({
            "action_type": "EMAIL_CANDIDATE",
            "target_id": "candidate-123",
            "reason": "Strong fit for backend role",
            "payload": proposal.payload,
        })
        assert "PENDING_APPROVAL" in result

    # Step 2: Cannot execute while pending
    with pytest.raises(Exception) as exc:
        await assert_action_approved(mock_db, str(proposal.id))
    assert "pending" in str(exc.value.detail).lower()

    # Step 3: Human approves
    proposal.status = ActionStatus.APPROVED
    proposal.approved_at = datetime.now(timezone.utc)
    proposal.approved_by = "00000000-0000-0000-0000-000000000001"
    mock_db.execute.return_value = create_mock_result(proposal)

    approved = await assert_action_approved(mock_db, str(proposal.id))
    assert approved.status == ActionStatus.APPROVED

    # Step 4: Execute approved action
    executed = await execute_action(
        mock_db,
        str(proposal.id),
        actor_user_id="00000000-0000-0000-0000-000000000001",
        actor_role="RECRUITER",
    )
    assert executed.status == ActionStatus.EXECUTED
    assert executed.execution_result is not None
    assert executed.execution_result["provider"] == "mock"
    assert "mock email" in executed.execution_result["message"].lower()
    assert mock_db.commit.called

    # Step 5: Duplicate execution blocked
    mock_db.execute.return_value = create_mock_result(executed)
    with pytest.raises(Exception) as exc:
        await assert_action_approved(mock_db, str(proposal.id))
    assert "already been executed" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_e2e_execute_endpoint_workflow(async_client, mock_db):
    """HTTP-level verification of approve-then-execute flow."""
    proposal = ActionProposal(
        id="cccccccc-1111-2222-3333-444444444444",
        action_type=ActionType.EMAIL_CANDIDATE,
        status=ActionStatus.PENDING_APPROVAL,
        payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello"},
    )
    mock_db.execute.return_value = create_mock_result(proposal)

    # Execute before approval -> 403
    resp = await async_client.post(f"/api/v1/approvals/{proposal.id}/execute")
    assert resp.status_code == 403

    # Approve
    proposal.status = ActionStatus.PENDING_APPROVAL
    mock_db.execute.return_value = create_mock_result(proposal)
    approve_resp = await async_client.post(f"/api/v1/approvals/{proposal.id}/approve")
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"

    # Execute after approval -> 200 EXECUTED
    proposal.status = ActionStatus.APPROVED
    mock_db.execute.return_value = create_mock_result(proposal)
    exec_resp = await async_client.post(f"/api/v1/approvals/{proposal.id}/execute")
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["status"] == "EXECUTED"
    assert data["execution_result"]["provider"] == "mock"
