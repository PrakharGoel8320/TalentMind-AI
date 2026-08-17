from sqlalchemy import Column, ForeignKey, JSON, Uuid, Float, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base
import uuid

class Match(Base):
    """
    Represents the intersection of a Candidate and a Job, storing the AI pipeline's 
    detailed ranking scores, explanations, and model versions used.
    """
    job_id = Column(Uuid(as_uuid=True), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(Uuid(as_uuid=True), ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Final fused score from 0-100
    final_score = Column(Float, nullable=False)
    
    # Detailed components (e.g. {"cross_encoder_score": 92.5, "skill_match_score": 85.0})
    score_components = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=False, default={})
    
    # Flags like KEYWORD_STUFFER, HONEYPOT_DETECTED
    flags = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=False, default=[])
    
    # Explanation JSON from ExplainabilityEngine
    explanation = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    
    # Telemetry
    pipeline_run_id = Column(String, nullable=True)
    model_versions = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)

    # Relationships
    job = relationship("Job", back_populates="matches")
    candidate = relationship("Candidate")
