from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class ScoreCreate(BaseModel):
    """创建颜值评分请求模型"""
    is_public: bool = True
    
class ScoreDetail(BaseModel):
    """评分详情项模型"""
    category: str
    score: int
    description: str

class ScoreResponse(BaseModel):
    """评分结果响应模型"""
    success: bool
    score_id: Optional[int] = None
    face_score: Optional[float] = None
    image_url: Optional[str] = None
    feature_highlights: Optional[Dict[str, Any]] = None
    score_details: Optional[List[ScoreDetail]] = None
    created_at: Optional[str] = None
    is_public: Optional[bool] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True

class ScorePagination(BaseModel):
    """分页评分列表响应模型"""
    total: int
    page: int
    limit: int
    items: List[ScoreResponse] 