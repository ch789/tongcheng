from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(32), nullable=False)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
