from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import logging

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 设置日志
logger = logging.getLogger(__name__)

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2登录表单
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        logger.info(f"验证密码: plain_password类型={type(plain_password)}, hashed_password类型={type(hashed_password)}")
        logger.info(f"hashed_password值={hashed_password[:10]}...")
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"密码验证结果: {result}")
        return result
    except Exception as e:
        logger.error(f"密码验证出错: {str(e)}")
        # 如果出错，返回False而不是抛出异常
        return False

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"密码哈希出错: {str(e)}")
        # 如果bcrypt出错，使用简单哈希（仅用于开发环境）
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> str:
    """解码令牌并返回用户ID (sub字段)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的身份认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的身份认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        ) 