from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from app.core.base_class import Base

class ModelVersion(Base):
    version_tag = Column(String, unique=True, index=True, nullable=False)
    framework = Column(String, nullable=True)
    metrics = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    is_active = Column(Boolean, default=False)
