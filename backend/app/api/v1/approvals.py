from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.database.session import get_db
from app.models.action import ActionProposal
from app.models.enums import ActionStatus
from app.schemas.action import ActionProposalResponse, ActionDecisionRequest
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ActionProposalResponse])
async def list_approvals(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all action proposals.
    """
    result = await db.execute(select(ActionProposal).order_by(ActionProposal.created_at.desc()).offset(skip).limit(limit))
    proposals = result.scalars().all()
    return proposals

@router.get("/{id}", response_model=ActionProposalResponse)
async def get_approval(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get a specific action proposal by ID.
    """
    import uuid
    try:
        uuid_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    result = await db.execute(select(ActionProposal).filter(ActionProposal.id == uuid_id))
    proposal = result.scalars().first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Action proposal not found")
    return proposal

@router.post("/{id}/approve", response_model=ActionProposalResponse)
async def approve_action(
    id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Approve an action proposal.
    """
    import uuid
    try:
        uuid_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    result = await db.execute(select(ActionProposal).filter(ActionProposal.id == uuid_id))
    proposal = result.scalars().first()
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Action proposal not found")
        
    if proposal.status != ActionStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail=f"Cannot approve action in state {proposal.status}")
        
    proposal.status = ActionStatus.APPROVED
    proposal.approved_at = datetime.now(timezone.utc)
    try:
        proposal.approved_by = uuid.UUID(current_user.user_id)
    except Exception:
        proposal.approved_by = None
    
    await db.commit()
    await db.refresh(proposal)
    return proposal

@router.post("/{id}/reject", response_model=ActionProposalResponse)
async def reject_action(
    id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Reject an action proposal.
    """
    import uuid
    try:
        uuid_id = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
        
    result = await db.execute(select(ActionProposal).filter(ActionProposal.id == uuid_id))
    proposal = result.scalars().first()
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Action proposal not found")
        
    if proposal.status != ActionStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail=f"Cannot reject action in state {proposal.status}")
        
    proposal.status = ActionStatus.REJECTED
    proposal.rejected_at = datetime.now(timezone.utc)
    try:
        proposal.rejected_by = uuid.UUID(current_user.user_id)
    except Exception:
        proposal.rejected_by = None
    
    await db.commit()
    await db.refresh(proposal)
    return proposal

@router.post("/{id}/execute", response_model=ActionProposalResponse)
async def execute_approved_action(
    id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Execute an APPROVED action proposal safely.
    """
    from app.services.action_executor import execute_action
    from app.core.exceptions import ForbiddenError, NotFoundError
    
    try:
        # execute_action handles the security boundary and the actual side effect
        proposal = await execute_action(
            db,
            id,
            actor_user_id=current_user.user_id,
            actor_role=current_user.role,
        )
        return proposal
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e.detail))
    except ValueError as e:
        # For validation errors or execution failures
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal execution error")
