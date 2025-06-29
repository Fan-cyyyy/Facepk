from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from db.base import Base

class FriendStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"

class UserFriend(Base):
    __tablename__ = "user_friends"

    relation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(FriendStatus), default=FriendStatus.PENDING)
    created_at = Column(DateTime, default=func.now()) 