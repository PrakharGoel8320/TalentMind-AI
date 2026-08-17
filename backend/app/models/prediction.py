from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.base_class import Base

class Prediction(Base):
    model_version_id = Column(Uuid(as_uuid=True), ForeignKey("modelversion.id", ondelete="SET NULL"), nullable=True, index=True)
    input_data = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)

    # Relationships
    model_version = relationship("ModelVersion")
