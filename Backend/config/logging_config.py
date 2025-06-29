import logging
import sys
from pathlib import Path
import os

# 修改导入方式，使用相对导入
from .settings import LOG_LEVEL

# 日志目录
log_dir = Path('./logs')
os.makedirs(log_dir, exist_ok=True)

# 日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 日志配置
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': log_format,
            'datefmt': date_format,
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': log_dir / 'app.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': True
        },
    }
}


def setup_logging():
    """初始化日志配置"""
    from logging.config import dictConfig
    dictConfig(logging_config)
    
    # 创建应用日志记录器
    logger = logging.getLogger("face_score_pk")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    return logger 