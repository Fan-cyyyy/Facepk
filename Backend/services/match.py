import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import math
import json

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
            
            # 设置浮点数比较的容忍度 - 减小容忍度，确保只有完全相同的分数才会判定为平局
            TOLERANCE = 0.00001
            
            # 从feature_data中获取beauty值
            challenger_feature_data = challenger_score.feature_data
            opponent_feature_data = opponent_score.feature_data
            
            # 输出原始特征数据，便于调试
            logger.info(f"挑战者特征数据: {json.dumps(challenger_feature_data, ensure_ascii=False)}")
            logger.info(f"对手特征数据: {json.dumps(opponent_feature_data, ensure_ascii=False)}")
            
            # 获取beauty值，确保类型正确
            challenger_beauty = float(challenger_feature_data.get("beauty", 0)) if challenger_feature_data else 0
            opponent_beauty = float(opponent_feature_data.get("beauty", 0)) if opponent_feature_data else 0
            
            # 确定胜负，使用beauty值而不是face_score
            challenger_beauty_val = float(challenger_beauty)
            opponent_beauty_val = float(opponent_beauty)
            
            # 输出日志，便于调试
            logger.info(f"PK对战：挑战者beauty={challenger_beauty_val}，对手beauty={opponent_beauty_val}")
            logger.info(f"PK对战：挑战者face_score={challenger_score.face_score}，对手face_score={opponent_score.face_score}")
            logger.info(f"Beauty差值: {challenger_beauty_val - opponent_beauty_val}")
            
            if abs(challenger_beauty_val - opponent_beauty_val) < TOLERANCE:
                # 分数差异在容忍度范围内，视为平局
                result = MatchResult.TIE
                points_changed = 3
                logger.info("判定结果：平局")
            elif challenger_beauty_val > opponent_beauty_val:
                result = MatchResult.WIN
                points_changed = 15  # 简单起见，固定加减分
                logger.info("判定结果：胜利")
            else:
                result = MatchResult.LOSE
                points_changed = -10
                logger.info("判定结果：失败")
            
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
                    "image_url": challenger_score.image_url,
                    "beauty": challenger_beauty_val
                },
                "opponent": {
                    "user_id": opponent.user_id,
                    "username": opponent.username,
                    "avatar_url": opponent.avatar_url,
                    "score": opponent_score.face_score,
                    "image_url": opponent_score.image_url,
                    "beauty": opponent_beauty_val
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
    
    async def get_match_history(self, user_id: int, page: int = 1, limit: int = 10) -> Dict:
        """获取用户的对战历史"""
        try:
            # 计算分页
            offset = (page - 1) * limit
            
            # 查询用户参与的所有对战（作为挑战者或被挑战者）
            matches = self.db.query(Match).filter(
                or_(
                    Match.challenger_id == user_id,
                    Match.opponent_id == user_id
                )
            ).order_by(desc(Match.matched_at)).offset(offset).limit(limit).all()
            
            # 获取总数
            total = self.db.query(Match).filter(
                or_(
                    Match.challenger_id == user_id,
                    Match.opponent_id == user_id
                )
            ).count()
            
            # 处理结果
            results = []
            for match in matches:
                # 获取挑战者和对手信息
                challenger = self.db.query(User).filter(User.user_id == match.challenger_id).first()
                opponent = self.db.query(User).filter(User.user_id == match.opponent_id).first()
                
                if not challenger or not opponent:
                    continue
                
                # 获取评分记录以获取beauty值
                challenger_score = self.db.query(Score).filter(Score.score_id == match.challenger_score_id).first()
                opponent_score = self.db.query(Score).filter(Score.score_id == match.opponent_score_id).first()
                
                challenger_beauty = float(challenger_score.feature_data.get("beauty", 0)) if challenger_score and challenger_score.feature_data else 0
                opponent_beauty = float(opponent_score.feature_data.get("beauty", 0)) if opponent_score and opponent_score.feature_data else 0
                
                # 从用户视角确定结果
                if match.challenger_id == user_id:
                    result = match.result.value
                    points_change = match.points_changed
                else:
                    # 如果用户是被挑战者，结果需要反转
                    if match.result == MatchResult.WIN:
                        result = MatchResult.LOSE.value
                        points_change = 0  # 被挑战者目前不计分
                    elif match.result == MatchResult.LOSE:
                        result = MatchResult.WIN.value
                        points_change = 0  # 被挑战者目前不计分
                    else:
                        result = MatchResult.TIE.value
                        points_change = 0  # 被挑战者目前不计分
                
                # 构建对战记录
                match_data = {
                    "match_id": match.match_id,
                    "challenger": {
                        "user_id": challenger.user_id,
                        "username": challenger.username,
                        "avatar_url": challenger.avatar_url,
                        "score": match.challenger_score,
                        "beauty": challenger_beauty
                    },
                    "opponent": {
                        "user_id": opponent.user_id,
                        "username": opponent.username,
                        "avatar_url": opponent.avatar_url,
                        "score": match.opponent_score,
                        "beauty": opponent_beauty
                    },
                    "result": result,
                    "points_change": points_change,
                    "matched_at": match.matched_at
                }
                
                results.append(match_data)
            
            return {
                "success": True,
                "data": results,
                "total": total,
                "page": page,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"获取对战历史异常: {e}")
            return {"success": False, "error": str(e)}
    
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
            
            # 获取beauty值
            challenger_beauty = float(challenger_score.feature_data.get("beauty", 0)) if challenger_score and challenger_score.feature_data else 0
            opponent_beauty = float(opponent_score.feature_data.get("beauty", 0)) if opponent_score and opponent_score.feature_data else 0
            
            challenger_rating = challenger.elo_rating if challenger.elo_rating is not None else 1500
            
            return {
                "match_id": match.match_id,
                "challenger": {
                    "user_id": challenger.user_id,
                    "username": challenger.username,
                    "avatar_url": challenger.avatar_url,
                    "score": match.challenger_score,
                    "image_url": challenger_score.image_url if challenger_score else "",
                    "beauty": challenger_beauty
                },
                "opponent": {
                    "user_id": opponent.user_id,
                    "username": opponent.username,
                    "avatar_url": opponent.avatar_url,
                    "score": match.opponent_score,
                    "image_url": opponent_score.image_url if opponent_score else "",
                    "beauty": opponent_beauty
                },
                "result": match.result.value,
                "points_change": match.points_changed,
                "new_rating": challenger_rating,
                "matched_at": match.matched_at
            }
            
        except Exception as e:
            logger.error(f"获取对战详情异常: {e}")
            return None 