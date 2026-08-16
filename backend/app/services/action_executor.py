from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.action import ActionProposal
from app.models.enums import ActionStatus
from app.core.exceptions import ForbiddenError, NotFoundError

async def assert_action_approved(db: AsyncSession, action_id: str) -> ActionProposal:
    """
    STRICT SECURITY GUARD: Validates that an action is explicitly APPROVED before execution.
    Raises ForbiddenError or NotFoundError.
    Returns the ActionProposal if authorized.
    """
    import uuid
    try:
        uuid_id = uuid.UUID(action_id)
    except ValueError:
        raise NotFoundError("Invalid action ID format.")
        
    result = await db.execute(select(ActionProposal).filter(ActionProposal.id == uuid_id))
    action = result.scalars().first()
    
    if not action:
        raise NotFoundError("Action proposal not found.")
        
    if action.status == ActionStatus.PENDING_APPROVAL:
        raise ForbiddenError("Action execution blocked: Action is pending approval.")
        
    if action.status == ActionStatus.REJECTED:
        raise ForbiddenError("Action execution blocked: Action was rejected.")
        
    if action.status == ActionStatus.CANCELLED:
        raise ForbiddenError("Action execution blocked: Action was cancelled.")
        
    if action.status == ActionStatus.EXECUTED:
        raise ForbiddenError("Action execution blocked: Action has already been executed.")
        
    if action.status != ActionStatus.APPROVED:
        raise ForbiddenError(f"Action execution blocked: Invalid state {action.status}.")
        
    return action

async def execute_action(
    db: AsyncSession,
    action_id: str,
    actor_user_id: str | None = None,
    actor_role: str | None = None,
) -> ActionProposal:
    """
    Executes an approved action by validating it with the safety boundary
    and dispatching to the appropriate service.
    """
    from app.services.email_service import send_email_action
    from datetime import datetime, timezone
    import traceback
    
    # 1. Strict security check - will raise if not exactly APPROVED
    action = await assert_action_approved(db, action_id)

    # 1.5. Minimal authorization boundary:
    # If an approver identity is present, only that approver or an admin can execute.
    if action.approved_by is not None and actor_role != "ADMIN":
        if not actor_user_id or str(action.approved_by) != str(actor_user_id):
            raise ForbiddenError("Action execution blocked: You are not authorized to execute this approved action.")
    
    # 2. Dispatch execution
    try:
        if action.action_type == "EMAIL_CANDIDATE":
            result = await send_email_action(action.payload or {})
        else:
            # Other actions are not implemented yet for this hackathon
            result = {"status": "success", "provider": "mock", "message": f"Simulated execution for {action.action_type}"}
            
        # 3. Mark as executed safely
        action.status = ActionStatus.EXECUTED
        action.executed_at = datetime.now(timezone.utc)
        action.execution_result = result
        action.provider = result.get("provider", "unknown")
        
    except Exception as e:
        # Action failed, do NOT mark executed. We store error for idempotency retry or failure state.
        # Following strict constraints: Only APPROVED -> EXECUTING -> EXECUTED, or APPROVED -> FAILED
        # For simplicity, we just keep it APPROVED but store error, or change to REJECTED.
        # Let's just log error to execution_error but leave it APPROVED so it can be fixed/retried.
        action.execution_error = str(e)
        raise ValueError(f"Execution failed: {str(e)}")
        
    await db.commit()
    await db.refresh(action)
    return action
