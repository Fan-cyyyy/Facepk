from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    user_id: int
    username: Optional[str] = None

class TokenPayload(BaseModel):
    """令牌负载模型"""
    refresh_token: str 