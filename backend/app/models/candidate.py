from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class Candidate(Base):
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    latest_resume_id = Column(Uuid(as_uuid=True), ForeignKey('resume.id', use_alter=True), nullable=True)
    profile_jsonb = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", foreign_keys="Resume.candidate_id", cascade="all, delete-orphan")
    pipeline_entries = relationship("PipelineEntry", back_populates="candidate", cascade="all, delete-orphan")
    feedbacks = relationship("RecruiterFeedback", back_populates="candidate", cascade="all, delete-orphan")
    matches = relationship("Match", cascade="all, delete-orphan")
