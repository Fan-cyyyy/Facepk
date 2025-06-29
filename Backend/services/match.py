import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import math

from models.match import Match, MatchResult
from models.score import Score
from models.user import User

logger = logging.getLogger(__name__)

class MatchService:
    """PK对战服务"""
    
    def __init__(self, db: Session):
        """初始化服务"""
        self.db = db
    
    async def create_match(self, challenger_id: int, opponent_id: int, score_id: int) -> Dict:
        """创建一场PK对战"""
        try:
            # 检查挑战者的分数记录
            challenger_score = self.db.query(Score).filter(
                Score.score_id == score_id,
                Score.user_id == challenger_id
            ).first()
            
            if not challenger_score:
                return {"success": False, "error": "找不到挑战者的评分记录"}
            
            # 获取对手的最新公开评分作为对战对象
            opponent_score = self.db.query(Score).filter(
                Score.user_id == opponent_id,
                Score.is_public.is_(True)
            ).order_by(desc(Score.scored_at)).first()
            
            if not opponent_score:
                return {"success": False, "error": "找不到对手的公开评分记录"}
            
            # 设置浮点数比较的容忍度
            TOLERANCE = 0.0001
            
            # 确定胜负，添加浮点数比较容忍度
            if challenger_score.face_score - opponent_score.face_score > TOLERANCE:
                result = MatchResult.WIN
                points_changed = 15  # 简单起见，固定加减分
            elif opponent_score.face_score - challenger_score.face_score > TOLERANCE:
                result = MatchResult.LOSE
                points_changed = -10
            else:
                # 分数差异在容忍度范围内，视为平局
                result = MatchResult.TIE
                points_changed = 3
            
            # 输出日志，便于调试
            logger.info(f"PK对战：挑战者分数={challenger_score.face_score}，对手分数={opponent_score.face_score}，结果={result.value}")
            
            # 更新用户分数
            challenger = self.db.query(User).filter(User.user_id == challenger_id).first()
            if not challenger:
                return {"success": False, "error": "找不到挑战者信息"}
                
            current_rating = challenger.elo_rating if challenger.elo_rating is not None else 1500
            new_rating = current_rating + points_changed
            
            # 如果评分低于0则设为0
            if new_rating < 0:
                new_rating = 0
                
            challenger.elo_rating = new_rating
            
            # 创建对战记录
            match_record = Match(
                challenger_id=challenger_id,
                opponent_id=opponent_id,
                challenger_score_id=challenger_score.score_id,
                opponent_score_id=opponent_score.score_id,
                challenger_score=challenger_score.face_score,
                opponent_score=opponent_score.face_score,
                result=result,
                points_changed=points_changed
            )
            
            self.db.add(match_record)
            self.db.commit()
            self.db.refresh(match_record)
            
            # 获取用户信息
            challenger = self.db.query(User).filter(User.user_id == challenger_id).first()
            opponent = self.db.query(User).filter(User.user_id == opponent_id).first()
            
            if not challenger or not opponent:
                return {"success": False, "error": "用户信息获取失败"}
            
            # 构建响应
            return {
                "success": True,
                "match_id": match_record.match_id,
                "challenger": {
                    "user_id": challenger.user_id,
                    "username": challenger.username,
                    "avatar_url": challenger.avatar_url,
                    "score": challenger_score.face_score,
                    "image_url": challenger_score.image_url
                },
                "opponent": {
                    "user_id": opponent.user_id,
                    "username": opponent.username,
                    "avatar_url": opponent.avatar_url,
                    "score": opponent_score.face_score,
                    "image_url": opponent_score.image_url
                },
                "result": match_record.result.value,
                "points_change": points_changed,
                "new_rating": new_rating,
                "matched_at": match_record.matched_at
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建对战异常: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_matches(self, user_id: int, page: int = 1, limit: int = 10, result: Optional[str] = None) -> Dict:
        """获取用户的对战历史"""
        try:
            # 构建查询
            query = self.db.query(Match).filter(
                or_(
                    Match.challenger_id == user_id,
                    Match.opponent_id == user_id
                )
            )
            
            # 按结果过滤
            if result:
                try:
                    match_result = MatchResult(result)
                    query = query.filter(Match.result == match_result)
                except ValueError:
                    pass
            
            # 计算总数
            total = query.count()
            
            # 分页
            matches = query.order_by(desc(Match.matched_at)).offset((page - 1) * limit).limit(limit).all()
            
            # 构建响应
            data = []
            for match in matches:
                # 判断当前用户是挑战者还是被挑战者
                is_challenger = match.challenger_id == user_id
                
                # 获取对手信息
                opponent_id = match.opponent_id if is_challenger else match.challenger_id
                opponent = self.db.query(User).filter(User.user_id == opponent_id).first()
                
                if not opponent:
                    continue
                
                # 计算结果
                match_result = match.result.value
                if not is_challenger:
                    # 反转结果
                    if match_result == "Win":
                        match_result = "Lose"
                    elif match_result == "Lose":
                        match_result = "Win"
                
                # 构建记录
                data.append({
                    "match_id": match.match_id,
                    "opponent": {
                        "user_id": opponent.user_id,
                        "username": opponent.username,
                        "avatar_url": opponent.avatar_url
                    },
                    "challenger_score": match.challenger_score if is_challenger else match.opponent_score,
                    "opponent_score": match.opponent_score if is_challenger else match.challenger_score,
                    "result": match_result,
                    "points_change": match.points_changed if is_challenger else -match.points_changed,
                    "matched_at": match.matched_at
                })
            
            return {
                "total": total,
                "page": page,
                "limit": limit,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"获取对战历史异常: {e}")
            return {
                "total": 0,
                "page": page,
                "limit": limit,
                "data": []
            }
    
    def get_match_by_id(self, match_id: int) -> Optional[Dict]:
        """获取对战详情"""
        try:
            # 查询对战记录
            match = self.db.query(Match).filter(Match.match_id == match_id).first()
            
            if not match:
                return None
            
            # 获取用户信息
            challenger = self.db.query(User).filter(User.user_id == match.challenger_id).first()
            opponent = self.db.query(User).filter(User.user_id == match.opponent_id).first()
            
            if not challenger or not opponent:
                return None
                
            # 获取评分记录
            challenger_score = self.db.query(Score).filter(Score.score_id == match.challenger_score_id).first()
            opponent_score = self.db.query(Score).filter(Score.score_id == match.opponent_score_id).first()
            
            challenger_rating = challenger.elo_rating if challenger.elo_rating is not None else 1500
            
            return {
                "match_id": match.match_id,
                "challenger": {
                    "user_id": challenger.user_id,
                    "username": challenger.username,
                    "avatar_url": challenger.avatar_url,
                    "score": match.challenger_score,
                    "image_url": challenger_score.image_url if challenger_score else ""
                },
                "opponent": {
                    "user_id": opponent.user_id,
                    "username": opponent.username,
                    "avatar_url": opponent.avatar_url,
                    "score": match.opponent_score,
                    "image_url": opponent_score.image_url if opponent_score else ""
                },
                "result": match.result.value,
                "points_change": match.points_changed,
                "new_rating": challenger_rating,
                "matched_at": match.matched_at
            }
            
        except Exception as e:
            logger.error(f"获取对战详情异常: {e}")
            return None 