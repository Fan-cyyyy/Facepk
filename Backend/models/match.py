from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from db.base import Base

class MatchResult(str, enum.Enum):
    WIN = "Win"
    LOSE = "Lose"
    TIE = "Tie"

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    challenger_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    challenger_score_id = Column(Integer, ForeignKey("scores.score_id"), nullable=False)
    opponent_score_id = Column(Integer, ForeignKey("scores.score_id"), nullable=False)
    challenger_score = Column(Float, nullable=False)
    opponent_score = Column(Float, nullable=False)
    result = Column(Enum(MatchResult), nullable=False)
    points_changed = Column(Integer, nullable=False)
    matched_at = Column(DateTime, default=func.now()) 