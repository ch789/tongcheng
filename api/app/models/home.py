from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime
from app.database import Base


class HomeContent(Base):
    __tablename__ = "home_content"

    id = Column(Integer, primary_key=True, index=True)
    slogan = Column(Text, nullable=True)
    announcement = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
