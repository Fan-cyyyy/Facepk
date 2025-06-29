from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# 创建匹配请求
class MatchCreate(BaseModel):
    opponent_id: int
    score_id: int

# 用户信息简略
class UserBrief(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None

# 对战详情中的用户信息
class MatchUser(UserBrief):
    score: float
    image_url: str

# 对战响应
class MatchResponse(BaseModel):
    match_id: int
    challenger: MatchUser
    opponent: MatchUser
    result: str  # "Win", "Lose", "Tie"
    points_change: int
    new_rating: int
    matched_at: datetime
    success: bool = True

# 对战历史记录简略
class MatchBrief(BaseModel):
    match_id: int
    opponent: UserBrief
    challenger_score: float
    opponent_score: float
    result: str
    points_change: int
    matched_at: datetime

# 对战分页
class MatchPagination(BaseModel):
    total: int
    page: int
    limit: int
    data: List[MatchBrief] 