from sqlalchemy import Column, ForeignKey, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base


class RecruitmentSession(Base):
    """Lightweight persistent recruitment context for agent memory."""
    job_id = Column(Uuid(as_uuid=True), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)
    state_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    events_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list)

    job = relationship("Job", backref="recruitment_sessions")
