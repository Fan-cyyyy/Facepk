from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
import logging
from sqlalchemy.sql import distinct

from db.session import get_db
from services.auth import get_current_user
from models.user import User
from models.score import Score
from sqlalchemy import func, desc

router = APIRouter(prefix="/rankings", tags=["排行榜"])
logger = logging.getLogger(__name__)

@router.get("/global")
async def get_global_rankings(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Any:
    """获取全球颜值排行榜"""
    
    logger.info(f"获取全球排行榜数据，页码: {page}, 每页数量: {limit}")
    
    try:
        # 直接查询所有公开照片的评分记录，按分数降序排序
        # 不需要再使用子查询去重，因为我们在上传时已经处理了图片哈希值
        query = db.query(
            Score.score_id,
            Score.user_id,
            Score.face_score,
            Score.image_url,
            Score.scored_at,
            User.username,
            User.nickname,
            User.avatar_url
        ).join(
            User, User.user_id == Score.user_id
        ).filter(
            Score.is_public == True
        ).order_by(
            desc(Score.face_score)
        )
        
        # 计算总记录数
        total = query.count()
        logger.info(f"排行榜总数据条数: {total}")
        
        # 分页
        results = query.offset((page - 1) * limit).limit(limit).all()
        
        # 格式化结果
        ranking_data = []
        for i, (score_id, user_id, face_score, image_url, scored_at, username, nickname, avatar_url) in enumerate(results):
            # 处理图片URL，确保使用正斜杠
            if image_url and not image_url.startswith('http'):
                # 确保路径使用正斜杠且有正确的前缀
                image_url = image_url.replace('\\', '/')
                if not image_url.startswith('/'):
                    image_url = f"/{image_url}"
            
            item = {
                "rank": (page - 1) * limit + i + 1,
                "user_id": user_id,
                "score_id": score_id,
                "username": username,
                "nickname": nickname or username,
                "avatar": avatar_url,
                "highest_score": face_score,
                "image_url": image_url,
                "scored_at": scored_at.isoformat() if scored_at else None
            }
            ranking_data.append(item)
            logger.info(f"添加排行榜数据: {item}")
        
        response = {
            "total": total,
            "page": page,
            "limit": limit,
            "data": ranking_data
        }
        logger.info(f"返回排行榜数据: {response}")
        return response
        
    except Exception as e:
        logger.error(f"获取排行榜数据出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取排行榜数据失败: {str(e)}"
        ) 