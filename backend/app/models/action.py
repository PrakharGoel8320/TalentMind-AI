from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, JSON, Uuid
from sqlalchemy.orm import relationship
from app.core.base_class import Base
from app.models.enums import ActionStatus, ActionType

class ActionProposal(Base):
    job_id = Column(Uuid(as_uuid=True), ForeignKey("job.id", ondelete="CASCADE"), nullable=True)
    agent_run_id = Column(String, nullable=True)
    
    action_type = Column(Enum(ActionType), nullable=False)
    target_id = Column(String, nullable=True)
    
    status = Column(Enum(ActionStatus), default=ActionStatus.PENDING_APPROVAL, nullable=False)
    payload = Column(JSON, nullable=True)
    reason = Column(String, nullable=True)
    
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    
    execution_result = Column(JSON, nullable=True)
    execution_error = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    
    approved_by = Column(Uuid(as_uuid=True), ForeignKey("user.id"), nullable=True)
    rejected_by = Column(Uuid(as_uuid=True), ForeignKey("user.id"), nullable=True)

    job = relationship("Job", backref="action_proposals")
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
