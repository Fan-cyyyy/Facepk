import os
import uuid
import base64
import requests
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import asyncio
import logging
from sqlalchemy.orm import Session
import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
    logging.error("OpenCV (cv2) 未安装，某些图像处理功能可能不可用")
from PIL import Image
import io

# 使用普通导入
from config import settings
from models.score import Score, ServiceType
from models.user import User

logger = logging.getLogger(__name__)

class ScoringService:
    """颜值评分服务"""
    
    def __init__(self, db: Session):
        """初始化服务"""
        self.db = db
        # 百度AI配置
        self.api_key = settings.BAIDU_AI_API_KEY
        self.secret_key = settings.BAIDU_AI_SECRET_KEY
        self.access_token = None
        # 图片存储路径
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    def get_access_token(self):
        """获取百度AI访问令牌"""
        if not self.api_key or not self.secret_key:
            logger.error("百度AI API密钥未配置")
            return None
            
        token_url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret_key
        }
        
        try:
            response = requests.post(token_url, params=params).json()
            self.access_token = response.get('access_token')
            return self.access_token
        except Exception as e:
            logger.error(f"获取access_token失败: {e}")
            return None
    
    def _calculate_image_hash(self, image_data: bytes) -> str:
        """计算图片的哈希值，用于识别相同图片"""
        try:
            # 使用MD5计算图片哈希值
            return hashlib.md5(image_data).hexdigest()
        except Exception as e:
            logger.error(f"计算图片哈希值失败: {e}")
            # 如果计算失败，返回一个随机值
            return uuid.uuid4().hex
    
    def _calculate_perceptual_hash(self, image_data: bytes) -> str:
        """计算图片的感知哈希值，用于识别相似图片"""
        if not CV2_AVAILABLE:
            return self._calculate_image_hash(image_data)
            
        try:
            # 将图片数据转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 调整大小为8x8
            img = cv2.resize(img, (8, 8))
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 计算平均值
            avg = gray.mean()
            # 生成哈希值
            hash_value = 0
            for i in range(8):
                for j in range(8):
                    hash_value = hash_value * 2 + (1 if gray[i, j] >= avg else 0)
            
            return hex(hash_value)[2:]
        except Exception as e:
            logger.error(f"计算感知哈希值失败: {e}, 将使用MD5哈希")
            return self._calculate_image_hash(image_data)
    
    def _find_similar_images(self, image_data: bytes) -> Optional[Score]:
        """查找相似图片"""
        # 计算图片哈希值
        image_hash = self._calculate_image_hash(image_data)
        
        # 查找完全相同的图片
        existing_score = self.db.query(Score).filter(
            Score.image_hash == image_hash,
            Score.is_public == True
        ).first()
        
        if existing_score:
            logger.info(f"找到完全相同的图片，哈希值: {image_hash}")
            return existing_score
        
        # 如果没有找到完全相同的图片，尝试计算感知哈希并查找相似图片
        if CV2_AVAILABLE:
            try:
                # 将图片数据转换为PIL图像对象
                img = Image.open(io.BytesIO(image_data))
                img = img.resize((100, 100)).convert('L')  # 调整大小并转为灰度
                img_array = np.array(img).flatten()
                
                # 获取所有公开图片
                all_scores = self.db.query(Score).filter(Score.is_public == True).all()
                
                for score in all_scores:
                    # 跳过没有图片路径的记录
                    if not score.image_url:
                        continue
                    
                    # 构建完整路径
                    image_path = score.image_url
                    if image_path.startswith('/'):
                        image_path = image_path[1:]  # 去除开头的斜杠
                    
                    # 尝试不同的路径组合
                    full_paths = [
                        os.path.join(settings.UPLOAD_FOLDER, os.path.basename(image_path)),
                        os.path.join(os.getcwd(), image_path),
                        os.path.join(os.getcwd(), settings.UPLOAD_FOLDER, os.path.basename(image_path))
                    ]
                    
                    for path in full_paths:
                        if os.path.exists(path):
                            try:
                                # 加载图片并计算相似度
                                other_img = Image.open(path)
                                other_img = other_img.resize((100, 100)).convert('L')
                                other_array = np.array(other_img).flatten()
                                
                                # 计算欧氏距离
                                dist = np.sqrt(np.sum((img_array - other_array) ** 2))
                                max_dist = np.sqrt(100 * 100 * 255 * 255)  # 最大可能距离
                                
                                # 转换为相似度（0-1之间）
                                similarity = 1 - (dist / max_dist)
                                
                                # 相似度阈值，可以根据需要调整
                                if similarity > 0.85:  # 85%相似度被认为是同一张图片
                                    logger.info(f"找到相似图片，相似度: {similarity:.4f}")
                                    return score
                            except Exception as e:
                                logger.error(f"计算图片相似度失败: {e}")
                                continue
            except Exception as e:
                logger.error(f"查找相似图片失败: {e}")
        
        return None
    
    def _save_image(self, image_data: bytes, user_id: int) -> str:
        """保存图片并返回URL"""
        # 生成唯一文件名
        filename = f"{user_id}_{uuid.uuid4()}.jpg"
        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
        
        # 保存图片
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # 返回相对URL（实际项目中可能需要CDN路径）
        return f"/uploads/{filename}"
    
    async def detect_face(self, image_data: bytes) -> Dict:
        """检测人脸并返回特征点"""
        try:
            # 获取access_token
            if not self.access_token:
                self.access_token = self.get_access_token()
                
            if not self.access_token:
                return {"success": False, "error": "无法获取百度AI访问令牌"}
                
            # 将图片编码为base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # 调用百度AI人脸检测接口V3
            detect_url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={self.access_token}"
            
            payload = {
                "image": image_base64,
                "image_type": "BASE64",
                "face_field": "age,beauty,expression,face_shape,gender,landmark"
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(detect_url, headers=headers, json=payload)
            result = response.json()
            
            logger.info(f"百度AI返回结果: {result}")
            
            # 检查返回结果
            if result.get('error_code', 0) != 0:
                logger.error(f"人脸检测失败: {result}")
                return {"success": False, "error": result.get('error_msg', '未知错误')}
            
            # 检查是否有人脸
            face_list = result.get('result', {}).get('face_list', [])
            if not face_list:
                return {"success": False, "error": "未检测到人脸"}
            
            # 返回检测结果
            return {"success": True, "face_info": face_list[0]}
            
        except Exception as e:
            logger.error(f"人脸检测异常: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_score(self, face_features: Dict) -> float:
        """基于特征计算颜值分数"""
        # 从百度AI返回的结果中提取beauty分数（0-100）
        beauty = face_features.get("beauty", 0)
        
        # 百度API的beauty分数已经是0-100之间，直接使用即可
        # 如果需要调整评分策略，可以在这里修改
        return beauty
    
    async def upload_and_score(self, user_id: int, image_data: bytes, is_public: bool) -> Dict:
        """上传图片并进行颜值评分"""
        try:
            # 1. 检测人脸
            face_detection = await self.detect_face(image_data)
            if not face_detection["success"]:
                return {"success": False, "error": face_detection["error"]}
            
            face_info = face_detection["face_info"]
            
            # 2. 计算颜值评分
            face_score = self.calculate_score(face_info)
            
            # 3. 计算图片哈希值
            image_hash = self._calculate_image_hash(image_data)
            
            # 4. 查找相似图片
            similar_score = self._find_similar_images(image_data)
            
            # 如果找到相似图片且新分数更高，则更新分数
            if similar_score:
                logger.info(f"发现相似图片，ID: {similar_score.score_id}, 哈希值: {similar_score.image_hash}")
                
                if face_score > similar_score.face_score:
                    logger.info(f"新分数({face_score})高于旧分数({similar_score.face_score})，更新记录")
                    
                    # 保存新图片
                    image_url = self._save_image(image_data, user_id)
                    
                    # 更新记录
                    similar_score.face_score = face_score
                    similar_score.feature_data = face_info
                    similar_score.scored_at = datetime.now()
                    similar_score.user_id = user_id  # 更新为当前用户
                    similar_score.image_url = image_url  # 更新图片URL
                    similar_score.image_hash = image_hash  # 更新哈希值
                    
                    self.db.commit()
                    self.db.refresh(similar_score)
                    
                    score_record = similar_score
                else:
                    logger.info(f"新分数({face_score})不高于旧分数({similar_score.face_score})，使用旧记录")
                    score_record = similar_score
            else:
                # 5. 保存图片
                image_url = self._save_image(image_data, user_id)
                
                # 6. 保存评分记录到数据库
                score_record = Score(
                    user_id=user_id,
                    image_url=image_url,
                    image_hash=image_hash,  # 保存图片哈希值
                    face_score=face_score,
                    feature_data=face_info,  # 保存完整特征数据
                    is_public=is_public,
                    service_type=ServiceType.BAIDU
                )
                
                self.db.add(score_record)
                self.db.commit()
                self.db.refresh(score_record)
            
            # 7. 准备返回结果
            # 从特征数据中提取重要指标
            feature_highlights = {
                "beauty": face_info.get("beauty", 0),
                "age": face_info.get("age", 0),
                "gender": face_info.get("gender", {}).get("type", "unknown"),
                "face_shape": face_info.get("face_shape", {}).get("type", "unknown"),
                "expression": face_info.get("expression", {}).get("type", "unknown")
            }
            
            # 构建详细评分项
            score_details = [
                {
                    "category": "颜值评分",
                    "score": int(face_score / 10),  # 转为1-10分
                    "description": self._get_beauty_description(face_score)
                },
                {
                    "category": "五官协调",
                    "score": min(10, int(face_score / 10) + (1 if face_score % 10 > 5 else 0)),
                    "description": "五官比例协调，轮廓清晰"
                },
                {
                    "category": "肤质",
                    "score": min(10, max(7, int(face_score / 12))),
                    "description": "肤色均匀，质地细腻"
                },
                {
                    "category": "气质", 
                    "score": min(10, max(6, int(face_score / 11))),
                    "description": "气质出众，形象佳"
                }
            ]
            
            return {
                "success": True,
                "score_id": score_record.score_id,
                "face_score": face_score,
                "image_url": score_record.image_url,
                "feature_highlights": feature_highlights,
                "score_details": score_details,
                "created_at": score_record.scored_at.isoformat(),
                "is_public": score_record.is_public
            }
            
        except Exception as e:
            logger.error(f"评分过程异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_beauty_description(self, score: float) -> str:
        """根据分数生成描述"""
        if score >= 90:
            return "颜值出众，形象完美"
        elif score >= 80:
            return "颜值上佳，形象良好"
        elif score >= 70:
            return "颜值不错，形象自然"
        elif score >= 60:
            return "颜值中等，形象一般"
        else:
            return "颜值尚可，形象有待提升"
    
    def get_user_scores(self, user_id: int, page: int, limit: int, only_public: bool = False) -> Dict:
        """获取用户历史评分记录"""
        # 构建查询
        query = self.db.query(Score).filter(Score.user_id == user_id)
        
        # 如果只查询公开记录
        if only_public:
            query = query.filter(Score.is_public == True)
        
        # 计算总数
        total = query.count()
        
        # 分页并按时间倒序
        scores = query.order_by(Score.scored_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        # 转换为字典列表
        score_list = []
        for score in scores:
            score_list.append({
                "score_id": score.score_id,
                "face_score": score.face_score,
                "image_url": score.image_url,
                "scored_at": score.scored_at.isoformat(),
                "is_public": score.is_public
            })
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "data": score_list
        }
    
    def get_score_by_id(self, score_id: int) -> Optional[Dict]:
        """获取单条评分详情"""
        score = self.db.query(Score).filter(Score.score_id == score_id).first()
        
        if not score:
            return None
        
        # 提取特征数据
        feature_data = score.feature_data or {}
        
        # 构建返回结果
        return {
            "score_id": score.score_id,
            "user_id": score.user_id,
            "face_score": score.face_score,
            "image_url": score.image_url,
            "feature_data": feature_data,
            "scored_at": score.scored_at.isoformat(),
            "is_public": score.is_public,
            "service_type": score.service_type
        } 