from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base
from app.models.enums import PipelineStage

class PipelineEntry(Base):
    job_id = Column(Uuid(as_uuid=True), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(Uuid(as_uuid=True), ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(SQLEnum(PipelineStage), default=PipelineStage.SOURCED, nullable=False, index=True)
    ranking_score = Column(Float, nullable=True, index=True)
    explanation = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    matched_skills = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    missing_skills = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    confidence = Column(Float, nullable=True)
    score_breakdown = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)

    # Relationships
    job = relationship("Job", back_populates="pipeline_entries")
    candidate = relationship("Candidate", back_populates="pipeline_entries")
