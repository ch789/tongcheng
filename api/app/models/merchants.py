from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
import enum
from datetime import datetime
from app.database import Base


class MerchantStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class MerchantApplication(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    shop_name = Column(String(128), nullable=False)
    business_license = Column(Text, nullable=True)  # 图片URL
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    area = Column(String(64), nullable=True)  # 所在区域
    industry_name = Column(String(64), nullable=True)  # 所属行业
    status = Column(SAEnum(MerchantStatus), default=MerchantStatus.PENDING_REVIEW, nullable=False)
    reject_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
