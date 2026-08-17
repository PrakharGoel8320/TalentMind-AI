from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base
from app.models.enums import JobStatus

class Job(Base):
    title = Column(String, nullable=False, index=True)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    skills = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.DRAFT, nullable=False, index=True)

    # Relationships
    pipeline_entries = relationship("PipelineEntry", back_populates="job", cascade="all, delete-orphan")
    feedbacks = relationship("RecruiterFeedback", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")
