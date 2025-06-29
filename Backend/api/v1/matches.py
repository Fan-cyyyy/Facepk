from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, Form
from sqlalchemy.orm import Session

from schemas.score import ScoreResponse
from schemas.match import MatchCreate, MatchResponse, MatchPagination
from services.match import MatchService
from services.auth import get_current_user
from models.user import User
from db.session import get_db

router = APIRouter(prefix="/matches", tags=["PK对战"])

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """发起PK对战"""
    match_service = MatchService(db)
    
    result = await match_service.create_match(
        challenger_id=current_user.user_id,
        opponent_id=match_data.opponent_id,
        score_id=match_data.score_id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result

@router.get("/user/{user_id}", response_model=MatchPagination)
async def get_user_matches(
    user_id: int,
    page: int = 1,
    limit: int = 10,
    result: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取用户的对战历史"""
    match_service = MatchService(db)
    
    matches = match_service.get_user_matches(
        user_id=user_id,
        page=page,
        limit=limit,
        result=result
    )
    
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match_detail(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """获取对战详情"""
    match_service = MatchService(db)
    match = match_service.get_match_by_id(match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对战记录不存在"
        )
    
    return match 