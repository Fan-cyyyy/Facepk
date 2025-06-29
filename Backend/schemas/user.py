from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """用户基本信息"""
    username: str
    email: EmailStr
    nickname: Optional[str] = None
    is_active: bool = True
    
class UserCreate(UserBase):
    """用户创建请求模型"""
    password: str = Field(..., min_length=8)
    avatar_url: Optional[str] = None
    
class UserUpdate(BaseModel):
    """用户更新请求模型"""
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    
class UserResponse(UserBase):
    """用户响应模型"""
    user_id: int
    avatar_url: Optional[str] = None
    elo_rating: Optional[int] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    token: Optional[str] = None
    token_type: Optional[str] = None
    
    class Config:
        from_attributes = True 