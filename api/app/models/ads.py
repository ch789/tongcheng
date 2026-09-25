from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.database import Base


class AdStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    image = Column(Text, nullable=False)
    link = Column(String(256), nullable=True)
    merchant_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(SAEnum(AdStatus), default=AdStatus.PENDING_REVIEW, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    merchant = relationship("User", backref="ads", foreign_keys=[merchant_id])
