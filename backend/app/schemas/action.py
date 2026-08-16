from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.enums import ActionStatus, ActionType

class ActionProposalBase(BaseModel):
    job_id: Optional[str] = None
    agent_run_id: Optional[str] = None
    action_type: ActionType
    target_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None

class ActionProposalCreate(ActionProposalBase):
    pass

class ActionProposalUpdate(BaseModel):
    status: ActionStatus

class ActionDecisionRequest(BaseModel):
    reason: Optional[str] = None

class ActionProposalResponse(ActionProposalBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    status: ActionStatus
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    approved_by: Optional[Any] = None
    rejected_by: Optional[Any] = None
    provider: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    execution_error: Optional[str] = None
