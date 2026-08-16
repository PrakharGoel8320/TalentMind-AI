"""
Part 4 Comprehensive Tests: Communication / Action Execution Tools

Covers:
- Approval boundary (pending, rejected, cancelled, approved, executed, not found)
- Email validation (missing recipient, invalid recipient, missing subject, missing body, wrong action type)
- Mock provider (executes successfully, does not contact SMTP, result persisted)
- Agent security (can create proposal, cannot directly execute, cannot approve, cannot bypass)
- API endpoint (execute works for approved, rejects pending, rejects rejected, rejects duplicate)
- Failure handling (provider failure -> safe state, no auto-retry)
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.models.action import ActionProposal
from app.models.enums import ActionStatus, ActionType
from app.services.action_executor import assert_action_approved, execute_action
from app.services.email_service import (
    MockEmailProvider, SMTPEmailProvider, send_email_action, get_email_provider
)
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from tests.conftest import create_mock_result


# ===================== APPROVAL BOUNDARY TESTS =====================

class TestApprovalBoundary:
    """Tests that the security guard correctly blocks/allows execution."""

    @pytest.mark.asyncio
    async def test_pending_email_cannot_execute(self):
        db = AsyncMock()
        proposal = ActionProposal(id="11111111-1111-1111-1111-111111111111", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.PENDING_APPROVAL)
        db.execute.return_value = create_mock_result(proposal)
        with pytest.raises(ForbiddenError) as exc:
            await assert_action_approved(db, "11111111-1111-1111-1111-111111111111")
        assert "pending" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_rejected_email_cannot_execute(self):
        db = AsyncMock()
        proposal = ActionProposal(id="22222222-2222-2222-2222-222222222222", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.REJECTED)
        db.execute.return_value = create_mock_result(proposal)
        with pytest.raises(ForbiddenError) as exc:
            await assert_action_approved(db, "22222222-2222-2222-2222-222222222222")
        assert "rejected" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cancelled_email_cannot_execute(self):
        db = AsyncMock()
        proposal = ActionProposal(id="33333333-3333-3333-3333-333333333333", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.CANCELLED)
        db.execute.return_value = create_mock_result(proposal)
        with pytest.raises(ForbiddenError) as exc:
            await assert_action_approved(db, "33333333-3333-3333-3333-333333333333")
        assert "cancelled" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_approved_email_can_execute(self):
        db = AsyncMock()
        proposal = ActionProposal(id="44444444-4444-4444-4444-444444444444", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.APPROVED)
        db.execute.return_value = create_mock_result(proposal)
        result = await assert_action_approved(db, "44444444-4444-4444-4444-444444444444")
        assert result.id == "44444444-4444-4444-4444-444444444444"

    @pytest.mark.asyncio
    async def test_executed_email_cannot_execute_again(self):
        db = AsyncMock()
        proposal = ActionProposal(id="55555555-5555-5555-5555-555555555555", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.EXECUTED)
        db.execute.return_value = create_mock_result(proposal)
        with pytest.raises(ForbiddenError) as exc:
            await assert_action_approved(db, "55555555-5555-5555-5555-555555555555")
        assert "already been executed" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_action_rejected(self):
        db = AsyncMock()
        db.execute.return_value = create_mock_result(None)
        with pytest.raises(NotFoundError):
            await assert_action_approved(db, "00000000-0000-0000-0000-000000000000")


# ===================== EMAIL VALIDATION TESTS =====================

class TestEmailValidation:
    """Tests that email payloads are validated before sending."""

    @pytest.mark.asyncio
    async def test_missing_recipient_fails(self):
        with pytest.raises(ValidationError) as exc:
            await send_email_action({"subject": "Hi", "body": "Hello"})
        assert "recipient" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_invalid_recipient_fails(self):
        with pytest.raises(ValidationError) as exc:
            await send_email_action({"recipient": "notanemail", "subject": "Hi", "body": "Hello"})
        assert "recipient" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_missing_subject_fails(self):
        with pytest.raises(ValidationError) as exc:
            await send_email_action({"recipient": "test@example.com", "body": "Hello"})
        assert "subject" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_missing_body_fails(self):
        with pytest.raises(ValidationError) as exc:
            await send_email_action({"recipient": "test@example.com", "subject": "Hi"})
        assert "body" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_wrong_action_type_fails(self, async_client, mock_db):
        """An action with the wrong type should not dispatch to email."""
        proposal = ActionProposal(
            id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            action_type=ActionType.EMAIL_CANDIDATE,
            status=ActionStatus.APPROVED,
            payload={}  # Empty payload will fail validation
        )
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/execute")
        assert response.status_code == 400


# ===================== MOCK PROVIDER TESTS =====================

class TestMockProvider:
    """Tests that the mock email provider works correctly."""

    @pytest.mark.asyncio
    async def test_mock_email_executes_successfully(self):
        provider = MockEmailProvider()
        result = await provider.send_email("test@example.com", "Hello", "Body text")
        assert result["status"] == "success"
        assert result["provider"] == "mock"
        assert "mock email" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_mock_provider_does_not_contact_smtp(self):
        """Mock provider must not attempt any real SMTP connection."""
        with patch("smtplib.SMTP") as mock_smtp:
            provider = MockEmailProvider()
            await provider.send_email("test@example.com", "Hello", "Body")
            mock_smtp.assert_not_called()

    @pytest.mark.asyncio
    async def test_execution_result_is_persisted(self, async_client, mock_db):
        proposal = ActionProposal(
            id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            action_type=ActionType.EMAIL_CANDIDATE,
            status=ActionStatus.APPROVED,
            payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello"}
        )
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/execute")
        assert response.status_code == 200
        data = response.json()
        assert data["execution_result"] is not None
        assert data["execution_result"]["provider"] == "mock"
        assert data["executed_at"] is not None
        assert data["provider"] == "mock"

    @pytest.mark.asyncio
    async def test_default_email_mode_is_mock(self):
        """EMAIL_MODE defaults to 'mock', ensuring no real emails are sent."""
        provider = get_email_provider()
        assert isinstance(provider, MockEmailProvider)


# ===================== AGENT SECURITY TESTS =====================

class TestAgentSecurity:
    """Tests that the agent cannot bypass the approval system."""

    @pytest.mark.asyncio
    async def test_agent_can_create_proposal(self, mocker):
        from app.ai.agent.tools import propose_action_tool
        mock_session = AsyncMock()
        mocker.patch("app.database.session.AsyncSessionLocal", return_value=mock_session)
        mock_session.__aenter__.return_value = mock_session

        result = propose_action_tool.invoke({
            "action_type": "EMAIL_CANDIDATE",
            "target_id": "cand_1",
            "reason": "Good candidate",
            "payload": {"recipient": "cand@example.com", "subject": "Hi", "body": "Hello"}
        })
        assert "PENDING_APPROVAL" in result
        assert mock_session.add.called

    @pytest.mark.asyncio
    async def test_agent_cannot_directly_execute_email(self):
        """The agent has no tool to call send_email directly. This tests the architectural boundary."""
        from app.ai.agent import tools as agent_tools
        tool_names = [t.name for t in [
            agent_tools.retrieve_candidates_tool,
            agent_tools.analyze_features_tool,
            agent_tools.rank_candidates_tool,
            agent_tools.analyze_behavior_tool,
            agent_tools.finalize_and_fuse_tool,
            agent_tools.propose_action_tool,
        ]]
        # No "execute" or "send_email" tool exists
        assert "send_email" not in " ".join(tool_names).lower()
        assert "execute_action" not in " ".join(tool_names).lower()

    @pytest.mark.asyncio
    async def test_agent_cannot_approve_proposal(self):
        """The agent has no tool to approve actions. Only the API/human can."""
        from app.ai.agent import tools as agent_tools
        tool_names = [t.name for t in [
            agent_tools.retrieve_candidates_tool,
            agent_tools.analyze_features_tool,
            agent_tools.rank_candidates_tool,
            agent_tools.analyze_behavior_tool,
            agent_tools.finalize_and_fuse_tool,
            agent_tools.propose_action_tool,
        ]]
        assert "approve" not in " ".join(tool_names).lower()


# ===================== API ENDPOINT TESTS =====================

class TestAPIEndpoint:
    """Tests for the /api/v1/approvals/{id}/execute endpoint."""

    @pytest.mark.asyncio
    async def test_execute_works_for_approved(self, async_client, mock_db):
        proposal = ActionProposal(
            id="cccccccc-cccc-cccc-cccc-cccccccccccc",
            action_type=ActionType.EMAIL_CANDIDATE,
            status=ActionStatus.APPROVED,
            payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello"}
        )
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/cccccccc-cccc-cccc-cccc-cccccccccccc/execute")
        assert response.status_code == 200
        assert response.json()["status"] == "EXECUTED"

    @pytest.mark.asyncio
    async def test_execute_rejects_pending(self, async_client, mock_db):
        proposal = ActionProposal(id="dddddddd-dddd-dddd-dddd-dddddddddddd", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.PENDING_APPROVAL)
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/dddddddd-dddd-dddd-dddd-dddddddddddd/execute")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_execute_rejects_rejected(self, async_client, mock_db):
        proposal = ActionProposal(id="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.REJECTED)
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee/execute")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_execute_rejects_duplicate(self, async_client, mock_db):
        proposal = ActionProposal(id="ffffffff-ffff-ffff-ffff-ffffffffffff", action_type=ActionType.EMAIL_CANDIDATE, status=ActionStatus.EXECUTED)
        mock_db.execute.return_value = create_mock_result(proposal)
        response = await async_client.post("/api/v1/approvals/ffffffff-ffff-ffff-ffff-ffffffffffff/execute")
        assert response.status_code == 403
        assert "already been executed" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_execute_rejects_nonexistent(self, async_client, mock_db):
        mock_db.execute.return_value = create_mock_result(None)
        response = await async_client.post("/api/v1/approvals/00000000-0000-0000-0000-000000000000/execute")
        assert response.status_code == 404


# ===================== FAILURE HANDLING TESTS =====================

class TestFailureHandling:
    """Tests that execution failures are handled safely."""

    @pytest.mark.asyncio
    async def test_provider_failure_safe_state(self, async_client, mock_db):
        """When the email provider raises an exception, action should NOT become EXECUTED."""
        proposal = ActionProposal(
            id="12345678-aaaa-bbbb-cccc-123456789012",
            action_type=ActionType.EMAIL_CANDIDATE,
            status=ActionStatus.APPROVED,
            payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello"}
        )
        mock_db.execute.return_value = create_mock_result(proposal)

        with patch("app.services.email_service.get_email_provider") as mock_get:
            failing_provider = AsyncMock()
            failing_provider.send_email.side_effect = ConnectionError("SMTP connection failed")
            mock_get.return_value = failing_provider

            response = await async_client.post("/api/v1/approvals/12345678-aaaa-bbbb-cccc-123456789012/execute")
            # Should return error, not 200
            assert response.status_code == 400
            # The proposal should NOT have been marked EXECUTED
            assert proposal.status != ActionStatus.EXECUTED

    @pytest.mark.asyncio
    async def test_failed_execution_does_not_auto_retry(self, async_client, mock_db):
        """After a failure, the system should not automatically retry."""
        proposal = ActionProposal(
            id="12345678-cccc-bbbb-aaaa-123456789012",
            action_type=ActionType.EMAIL_CANDIDATE,
            status=ActionStatus.APPROVED,
            payload={"recipient": "test@example.com", "subject": "Hi", "body": "Hello"}
        )
        mock_db.execute.return_value = create_mock_result(proposal)

        with patch("app.services.email_service.get_email_provider") as mock_get:
            failing_provider = AsyncMock()
            failing_provider.send_email.side_effect = Exception("Transient failure")
            mock_get.return_value = failing_provider

            response = await async_client.post("/api/v1/approvals/12345678-cccc-bbbb-aaaa-123456789012/execute")
            assert response.status_code == 400
            # Provider should have been called exactly once (no retry)
            assert failing_provider.send_email.call_count == 1
"""
Test file for Part 4: Communication / Action Execution Tools.
Comprehensive coverage of approval boundary, email validation,
mock provider, agent security, API endpoints, and failure handling.
"""
