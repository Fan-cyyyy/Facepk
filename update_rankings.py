import os
import sys
import logging
import random
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置和模型
from Backend.config.settings import DATABASE_URL
from Backend.models.user import User
from Backend.models.score import Score
from Backend.models.score import ServiceType
from Backend.db.base import Base

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_rankings():
    """更新排行榜数据，添加uploads中的图片"""
    try:
        # 创建SQLite数据库引擎
        engine = create_engine(DATABASE_URL)
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 获取uploads目录中的所有jpg文件
            uploads_dir = Path("Backend/uploads")
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
                
            # 清空原有的评分记录（可选，如果你想保留原有数据，可以注释掉这部分）
            # db.query(Score).delete()
            # logger.info("已清空原有评分记录")
            
            # 为每张图片分配一个随机用户并生成随机分数
            image_scores = []
            
            # 图片1 - 最高分
            user1 = random.choice(users)
            image1 = image_files[0]
            image_url1 = f"/uploads/{image1.name}"
            face_score1 = round(random.uniform(95, 99), 1)  # 高分
            
            # 图片2 - 中等分
            user2 = random.choice(users)
            image2 = image_files[1]
            image_url2 = f"/uploads/{image2.name}"
            face_score2 = round(random.uniform(80, 85), 1)  # 中等分
            
            # 图片3 - 低分
            user3 = random.choice(users) 
            image3 = image_files[2]
            image_url3 = f"/uploads/{image3.name}"
            face_score3 = round(random.uniform(60, 75), 1)  # 低分
            
            # 创建评分记录
            image_scores = [
                {"user": user1, "image_url": image_url1, "score": face_score1},
                {"user": user2, "image_url": image_url2, "score": face_score2},
                {"user": user3, "image_url": image_url3, "score": face_score3}
            ]
            
            # 添加到数据库
            for item in image_scores:
                # 创建并添加评分记录
                db_score = Score(
                    user_id=item["user"].user_id,
                    image_url=item["image_url"],
                    face_score=item["score"],
                    is_public=True,
                    service_type=ServiceType.BAIDU
                )
                db.add(db_score)
                logger.info(f"为用户 {item['user'].username} 添加评分记录: {item['score']} 分, 图片: {item['image_url']}")
            
            # 提交数据
            db.commit()
            logger.info("排行榜数据更新完成!")
            
            # 验证数据更新
            score_count = db.query(Score).count()
            logger.info(f"当前评分记录总数: {score_count}")
            
            # 输出排行榜
            logger.info("当前排行榜状态:")
            rankings = db.query(User.username, Score.face_score, Score.image_url)\
                       .join(Score, User.user_id == Score.user_id)\
                       .order_by(Score.face_score.desc())\
                       .limit(10).all()
            
            for i, (username, score, image_url) in enumerate(rankings):
                logger.info(f"{i+1}. {username}: {score} 分 - {image_url}")
                
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
    update_rankings() 