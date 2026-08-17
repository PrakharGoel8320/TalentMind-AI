from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
import enum
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class FeedbackAction(str, enum.Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    HIRED = "hired"

class RecruiterFeedback(Base):
    candidate_id = Column(Uuid(as_uuid=True), ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Uuid(as_uuid=True), ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Target of the feedback (e.g., "copilot_response", "candidate_summary", "ranking")
    target_type = Column(String, nullable=True)
    target_id = Column(String, nullable=True)
    
    # Action/Rating
    action = Column(SQLEnum(FeedbackAction), nullable=False, default=FeedbackAction.THUMBS_UP)
    is_helpful = Column(Boolean, nullable=True) # Legacy backward compatibility
    comments = Column(String, nullable=True)
    
    # LLM/Prompt Context for future DPO
    model_version = Column(String, nullable=True)
    prompt_type = Column(String, nullable=True)
    prompt_version = Column(String, nullable=True)
    dataset_version = Column(String, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="feedbacks")
    job = relationship("Job", back_populates="feedbacks")
    user = relationship("User")
