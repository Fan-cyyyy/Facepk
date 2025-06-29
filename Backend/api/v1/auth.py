from datetime import timedelta
from typing import Any
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.token import Token, TokenPayload
from schemas.user import UserCreate, UserResponse
from services.auth import AuthService
from db.session import get_db

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """注册新用户"""
    logger.info(f"收到注册请求: {user_data.dict(exclude={'password'})}")
    try:
        auth_service = AuthService(db)
        user = auth_service.register_user(user_data)
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            int(user.user_id), expires_delta=access_token_expires
        )
        
        response_data = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
            "token": access_token,
            "token_type": "bearer",
            "created_at": user.created_at
        }
        logger.info(f"用户注册成功: {user.username}")
        return response_data
    except HTTPException as e:
        logger.error(f"注册失败 (HTTP异常): {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"注册失败 (未处理异常): {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册过程中发生错误: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    auth_service.update_last_login(int(user.user_id))
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        int(user.user_id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username,
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: TokenPayload,
    db: Session = Depends(get_db)
) -> Any:
    """刷新访问令牌"""
    auth_service = AuthService(db)
    user_id = auth_service.validate_token(token.refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        user_id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    } 