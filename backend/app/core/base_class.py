import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

Base = declarative_base(cls=CustomBase)
