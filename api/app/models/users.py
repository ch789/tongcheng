from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import ENUM
import enum
from datetime import datetime
from app.database import Base


class UserRole(str, enum.Enum):
    VISITOR = "visitor"
    USER = "user"
    MERCHANT = "merchant"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(128), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    password_hash = Column(String(256), nullable=True)
    nickname = Column(String(64), nullable=True)
    avatar_url = Column(Text, nullable=True)
    role = Column(ENUM(UserRole), default=UserRole.VISITOR, nullable=False)
    is_disabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
