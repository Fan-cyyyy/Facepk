import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# API配置
API_V1_STR = "/api/v1"
PROJECT_NAME = "Magic Mirror Face Score PK"
VERSION = "1.0.0"

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
ALGORITHM = "HS256"

# 数据库配置
# 优先使用环境变量中的数据库URL，如果不存在则使用SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./face_score_pk.db")
# 如果环境变量指定了MySQL但我们想强制使用SQLite，取消下面这行的注释
DATABASE_URL = "sqlite:///./face_score_pk.db"
TEST_DATABASE_URL = "sqlite:///./test_face_score_pk.db"

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# 百度AI配置
BAIDU_AI_APP_ID = os.getenv("BAIDU_AI_APP_ID")
BAIDU_AI_API_KEY = os.getenv("BAIDU_AI_API_KEY")
BAIDU_AI_SECRET_KEY = os.getenv("BAIDU_AI_SECRET_KEY")

# 上传配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

# CORS设置
BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
    "https://mirror-pk.com",
]

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 