from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from db.base import Base

class UserStats(Base):
    __tablename__ = "user_stats"

    stat_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    matches_total = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    matches_lost = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    highest_score = Column(Float, default=0.0)
    rank_global = Column(Integer, nullable=True)
    rank_regional = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now()) 