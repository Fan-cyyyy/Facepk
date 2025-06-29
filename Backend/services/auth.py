"""
用户认证服务
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.session import get_db
from models.user import User
from schemas.user import UserCreate
from core.security import oauth2_scheme, decode_token, verify_password, get_password_hash, create_access_token

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    根据令牌获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解析令牌，获取用户ID
    try:
        user_id = decode_token(token)
        if user_id is None:
            raise credentials_exception
    except:
        raise credentials_exception
        
    # 根据用户ID查询用户
    try:
        user_id_int = int(user_id)
        user = db.query(User).filter(User.user_id == user_id_int).first()
        if user is None:
            raise credentials_exception
    except ValueError:
        # 如果无法转换为整数，可能是旧令牌，尝试通过username查询
        user = db.query(User).filter(User.username == user_id).first()
        if user is None:
            raise credentials_exception
        
    return user

class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        """初始化服务"""
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> User:
        """注册新用户"""
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
        
        # 创建新用户
        try:
            # 密码哈希处理
            hashed_password = get_password_hash(user_data.password)
            
            # 创建用户记录
            db_user = User(
                username=user_data.username,
                password_hash=hashed_password,
                email=user_data.email,
                nickname=user_data.nickname or user_data.username,
                avatar_url=user_data.avatar_url
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户创建失败，请检查输入信息"
            )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        # 确保将密码哈希转换为字符串
        if not verify_password(password, str(user.password_hash)):
            return None
            
        return user
    
    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        return create_access_token(subject=user_id, expires_delta=expires_delta)
    
    def update_last_login(self, user_id: int) -> None:
        """更新用户最后登录时间"""
        # 获取当前时间
        current_time = datetime.utcnow()
        
        # 执行更新操作
        self.db.query(User).filter(User.user_id == user_id).update(
            {"last_login": current_time}
        )
        self.db.commit()
    
    def validate_token(self, token: str) -> Optional[int]:
        """验证令牌有效性并返回用户ID"""
        try:
            user_id = decode_token(token)
            return int(user_id)
        except:
            return None 