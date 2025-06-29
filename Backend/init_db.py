import os
import sys
import logging
import random
import glob
import hashlib
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from config.settings import DATABASE_URL
from config.database import Base
from core.security import get_password_hash

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库"""
    try:
        # 创建SQLite数据库引擎
        engine = create_engine(DATABASE_URL)
        
        # 导入所有模型，确保它们已经注册到Base.metadata
        # 这里导入是为了确保模型类被加载
        from models.user import User
        from models.score import Score
        from models.match import Match
        
        # 创建所有表
        logger.info("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        
        # 检查表是否创建成功
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"已创建的表: {tables}")
        
        # 创建会话
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 检查是否已经有用户数据
            user_count = db.query(User).count()
            logger.info(f"当前用户数量: {user_count}")
            
            if user_count == 0:
                logger.info("添加初始用户数据...")
                # 创建一些初始用户
                initial_users = [
                    {
                        "username": "admin",
                        "email": "admin@example.com",
                        "password": "admin123",
                        "nickname": "管理员",
                        "is_active": True
                    },
                    {
                        "username": "user1",
                        "email": "user1@example.com",
                        "password": "user123",
                        "nickname": "用户1",
                        "is_active": True
                    },
                    {
                        "username": "user2",
                        "email": "user2@example.com",
                        "password": "user123",
                        "nickname": "用户2",
                        "is_active": True
                    },
                    {
                        "username": "user3",
                        "email": "user3@example.com",
                        "password": "user123",
                        "nickname": "用户3",
                        "is_active": True
                    },
                    {
                        "username": "user4",
                        "email": "user4@example.com",
                        "password": "user123",
                        "nickname": "用户4",
                        "is_active": True
                    },
                    {
                        "username": "user5",
                        "email": "user5@example.com",
                        "password": "user123",
                        "nickname": "用户5",
                        "is_active": True
                    }
                ]
                
                # 添加用户到数据库
                for user_data in initial_users:
                    try:
                        # 使用安全的密码哈希方法
                        hashed_password = get_password_hash(user_data["password"])
                        logger.info(f"为用户 {user_data['username']} 创建密码哈希: {hashed_password[:20]}...")
                    except Exception as e:
                        # 如果密码哈希失败，使用简单哈希（仅用于开发环境）
                        logger.error(f"密码哈希失败: {str(e)}，使用简单哈希代替")
                        hashed_password = hashlib.sha256(user_data["password"].encode()).hexdigest()
                    
                    db_user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=hashed_password,
                        nickname=user_data["nickname"],
                        is_active=user_data["is_active"]
                    )
                    db.add(db_user)
                    logger.info(f"添加用户: {user_data['username']}")
                
                # 提交用户数据
                db.commit()
                logger.info("初始用户数据添加完成!")
            
            # 检查是否已经有评分数据
            score_count = db.query(Score).count()
            logger.info(f"当前评分记录数量: {score_count}")
            
            if score_count == 0:
                logger.info("添加初始排行榜数据...")
                
                # 确保uploads目录存在
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(exist_ok=True)
                
                # 获取所有已有的示例图片
                example_images = []
                
                # 使用glob获取所有jpg文件
                image_files = glob.glob("uploads/*.jpg")
                if image_files:
                    example_images = image_files
                    logger.info(f"找到 {len(example_images)} 张图片: {example_images[:5]}...")
                
                # 如果没有足够的示例图片，使用默认图片
                if len(example_images) < 5:
                    logger.warning("示例图片不足，将使用默认图片URL")
                    example_images = [
                        "https://randomuser.me/api/portraits/men/1.jpg",
                        "https://randomuser.me/api/portraits/women/2.jpg",
                        "https://randomuser.me/api/portraits/men/3.jpg",
                        "https://randomuser.me/api/portraits/women/4.jpg",
                        "https://randomuser.me/api/portraits/men/5.jpg",
                        "https://randomuser.me/api/portraits/women/6.jpg",
                        "https://randomuser.me/api/portraits/men/7.jpg",
                        "https://randomuser.me/api/portraits/women/8.jpg",
                        "https://randomuser.me/api/portraits/men/9.jpg",
                        "https://randomuser.me/api/portraits/women/10.jpg",
                    ]
                
                # 为每个用户添加评分记录
                users = db.query(User).all()
                logger.info(f"为 {len(users)} 个用户添加评分记录")
                
                for user in users:
                    # 为每个用户添加1-3条评分记录
                    for _ in range(random.randint(1, 3)):
                        # 随机选择一张图片
                        image_url = random.choice(example_images)
                        
                        # 生成一个随机分数 (70-98)
                        face_score = round(random.uniform(70, 98), 1)
                        
                        # 创建评分记录
                        db_score = Score(
                            user_id=user.user_id,
                            image_url=image_url,
                            face_score=face_score,
                            is_public=True
                        )
                        db.add(db_score)
                        logger.info(f"为用户 {user.username} 添加评分记录: {face_score} 分, 图片: {image_url}")
                
                # 提交评分数据
                db.commit()
                logger.info("初始排行榜数据添加完成!")
                
                # 验证数据是否添加成功
                user_count = db.query(User).count()
                score_count = db.query(Score).count()
                logger.info(f"验证数据: 用户数量={user_count}, 评分记录数量={score_count}")
        
        except Exception as e:
            logger.error(f"初始化数据时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            raise
        finally:
            db.close()
        
        logger.info("数据库初始化完成!")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    init_db()
    print("数据库表已创建!") 