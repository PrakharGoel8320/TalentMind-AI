from sqlalchemy import Column, Float, String, Boolean, ForeignKey, Enum as SQLEnum, JSON, Uuid
from app.core.base_class import Base
from app.models.enums import UserRole

class User(Base):
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.RECRUITER, nullable=False)
    is_active = Column(Boolean, default=True)
