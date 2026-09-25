from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
import enum
from datetime import datetime
from app.database import Base


class ProductStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    OFF_SHELF = "off_shelf"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    images = Column(ARRAY(String), default=list)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    area = Column(String(64), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    view_count = Column(Integer, default=0, nullable=False)
    status = Column(SAEnum(ProductStatus), default=ProductStatus.PENDING_REVIEW, nullable=False)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("User", backref="products", foreign_keys=[merchant_id])
    industry = relationship("Industry", backref="products")
