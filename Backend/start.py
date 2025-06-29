import os
import sys
import subprocess
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """初始化数据库并启动服务器"""
    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        from init_db import init_db
        init_result = init_db()
        
        if not init_result:
            logger.error("数据库初始化失败，无法启动服务器")
            return
        
        # 启动服务器
        logger.info("启动服务器...")
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
        
    except Exception as e:
        logger.error(f"启动失败: {e}")

if __name__ == "__main__":
    main() 