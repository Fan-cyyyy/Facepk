import os
import sys
import uuid
import random
import base64
import asyncio
import requests
import logging
from pathlib import Path
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入模型
from models.user import User
from models.score import Score
from models.score import ServiceType
from db.base import Base
from config.settings import BAIDU_AI_API_KEY, BAIDU_AI_SECRET_KEY

# 百度AI配置
api_key = BAIDU_AI_API_KEY or "eb8uJZjrOrLwa5acw59JbxGw"  # 使用默认值，实际应从环境变量获取
secret_key = BAIDU_AI_SECRET_KEY or "X5YB0qlJuZjyCEKHPhFEQs0RJWitWbj7"  # 使用默认值，实际应从环境变量获取

def get_access_token():
    """获取百度AI访问令牌"""
    token_url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    
    try:
        response = requests.post(token_url, params=params).json()
        access_token = response.get('access_token')
        return access_token
    except Exception as e:
        logger.error(f"获取access_token失败: {e}")
        return None

async def detect_face(image_path: str) -> dict:
    """使用百度AI检测人脸并返回特征"""
    try:
        # 获取access_token
        access_token = get_access_token()
        
        if not access_token:
            return {"success": False, "error": "无法获取百度AI访问令牌"}
        
        # 读取图片并转为base64
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 调用百度AI人脸检测接口V3
        detect_url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={access_token}"
        
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

def calculate_score(face_features: dict) -> float:
    """基于特征计算颜值分数"""
    # 从百度AI返回的结果中提取beauty分数（0-100）
    beauty = face_features.get("beauty", 0)
    
    # 百度API的beauty分数已经是0-100之间，直接使用即可
    return beauty

async def update_rankings():
    """更新排行榜数据，添加uploads中的图片并使用百度AI进行评分"""
    try:
        # 创建SQLite数据库引擎
        engine = create_engine('sqlite:///face_score_pk.db')
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 获取uploads目录中的所有jpg文件
            uploads_dir = Path("uploads")
            image_files = list(uploads_dir.glob("*.jpg"))
            logger.info(f"找到 {len(image_files)} 张图片: {[f.name for f in image_files]}")
            
            if not image_files:
                logger.error("未找到任何图片文件！")
                return False
                
            # 获取用户列表
            users = db.query(User).all()
            if not users:
                logger.error("数据库中没有用户，请先运行init_db.py初始化数据库")
                return False
                
            # 清理现有的评分数据，确保每张图片只有一个评分记录
            db.query(Score).delete()
            db.commit()
            
            # 图片和用户的固定映射
            image_user_mapping = {
                "1_02ab9c6c-702a-4336-b4ea-55e60dbc7398.jpg": 3,  # user2
                "1_31e59d2f-6f3b-443a-a8c3-ef3284413487.jpg": 4,  # user3
                "1_74abab7d-eab5-4043-9553-b9b3c1daf6dd.jpg": 5,  # user4
            }
            
            # 为每张图片分配指定用户并使用百度AI进行评分
            for img in image_files:
                img_name = img.name
                user_id = image_user_mapping.get(img_name)
                
                if not user_id:
                    logger.warning(f"图片 {img_name} 没有指定用户，跳过")
                    continue
                
                # 获取用户
                user = db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    logger.warning(f"找不到用户ID {user_id}，跳过图片 {img_name}")
                    continue
                
                img_path = str(img.absolute())
                img_url = f"/uploads/{img.name}"
                
                # 调用百度AI进行人脸检测和颜值评分
                face_detection = await detect_face(img_path)
                if not face_detection["success"]:
                    logger.error(f"图片 {img.name} 评分失败: {face_detection['error']}")
                    continue
                
                face_info = face_detection["face_info"]
                
                # 计算颜值评分
                face_score = calculate_score(face_info)
                logger.info(f"图片 {img.name} 的颜值评分: {face_score}")
                
                # 创建评分记录
                db_score = Score(
                    user_id=user.user_id,
                    image_url=img_url,
                    face_score=face_score,
                    feature_data=face_info,
                    is_public=True,
                    service_type=ServiceType.BAIDU
                )
                db.add(db_score)
                logger.info(f"添加图片: {img_url}, 分数: {face_score}, 用户: {user.username}")
            
            # 提交更改
            db.commit()
            logger.info("排行榜数据更新完成!")
            
            # 输出当前排行榜
            rankings = db.query(User.username, Score.face_score, Score.image_url)\
                    .join(Score, User.user_id == Score.user_id)\
                    .order_by(desc(Score.face_score))\
                    .limit(10).all()
            
            print("\n当前排行榜:")
            for i, (username, score, image_url) in enumerate(rankings):
                print(f"{i+1}. {username}: {score} 分 - {image_url}")
                
            return True
                
        except Exception as e:
            logger.error(f"更新排行榜数据时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"连接数据库失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    asyncio.run(update_rankings()) 