from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.database import Base


class ActivityStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    REGISTERING = "registering"
    ENDED = "ended"
    OFF_SHELF = "off_shelf"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    cover_image = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(256), nullable=True)
    content = Column(Text, nullable=True)
    max_participants = Column(Integer, default=0, nullable=False)  # 0=不限
    status = Column(SAEnum(ActivityStatus), default=ActivityStatus.UPCOMING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    registrations = relationship("ActivityRegistration", backref="activity", foreign_keys="ActivityRegistration.activity_id")


class ActivityRegistration(Base):
    __tablename__ = "activity_registrations"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 游客可匿名报名
    register_type = Column(String(20), nullable=False)  # personal / merchant
    name = Column(String(64), nullable=False)
    phone = Column(String(20), nullable=False)
    area = Column(String(64), nullable=False)
    interest = Column(Text, nullable=True)
    remark = Column(Text, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
