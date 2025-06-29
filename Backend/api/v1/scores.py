from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from schemas.score import ScoreResponse, ScoreCreate, ScorePagination
from services.scoring import ScoringService
from services.auth import get_current_user
from models.user import User
from db.session import get_db

router = APIRouter(prefix="/scores", tags=["颜值评分"])

@router.post("/", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_score(
    image: UploadFile = File(...),
    is_public: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """上传图片并进行颜值评分"""
    scoring_service = ScoringService(db)
    
    # 读取图片数据
    image_data = await image.read()
    
    # 保存并评分
    result = await scoring_service.upload_and_score(
        user_id=current_user.user_id,
        image_data=image_data,
        is_public=is_public
    )
    
    return result

@router.get("/", response_model=ScorePagination)
async def get_scores(
    user_id: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取评分记录"""
    scoring_service = ScoringService(db)
    
    # 如果未指定用户ID，则默认为当前用户
    target_user_id = user_id if user_id else current_user.user_id
    
    # 非本人只能查询公开记录
    is_owner = target_user_id == current_user.user_id
    
    result = scoring_service.get_user_scores(
        user_id=target_user_id,
        page=page,
        limit=limit,
        only_public=not is_owner
    )
    
    return result

@router.get("/{score_id}", response_model=ScoreResponse)
async def get_score_detail(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取单条评分详情"""
    scoring_service = ScoringService(db)
    score = scoring_service.get_score_by_id(score_id)
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评分记录不存在"
        )
    
    # 检查访问权限
    if score.user_id != current_user.user_id and not score.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此评分记录"
        )
    
    return score 