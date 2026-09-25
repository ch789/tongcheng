"""Industry 行业字典"""
from sqlalchemy import Column, Integer, String
from app.database import Base


class Industry(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
