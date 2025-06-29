from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
import enum

from db.base import Base

class ServiceType(str, enum.Enum):
    BAIDU = "baidu"
    LOCAL = "local"

class Score(Base):
    __tablename__ = "scores"

    score_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    image_hash = Column(String(64), nullable=True)
    face_score = Column(Float, nullable=False)
    feature_data = Column(JSON, nullable=True)
    scored_at = Column(DateTime, default=func.now())
    is_public = Column(Boolean, default=True)
    service_type = Column(Enum(ServiceType), default=ServiceType.BAIDU) 