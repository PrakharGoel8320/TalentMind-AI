from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid, Integer
from app.core.base_class import Base

class DatasetVersion(Base):
    version_tag = Column(String, unique=True, index=True, nullable=False)
    s3_path = Column(String, nullable=False)
    row_count = Column(Integer, nullable=True)
