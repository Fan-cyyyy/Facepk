#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
清理数据库中的重复图片记录
只保留每个图片哈希值中分数最高的那条记录
"""

import os
import sys
import logging
from sqlalchemy import func, desc, create_engine, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import Session, sessionmaker
import hashlib
from PIL import Image
import io
import sqlite3

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入项目模块
from Backend.models.score import Score
from Backend.config.settings import DATABASE_URL

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_database_records():
    """显示数据库中的记录"""
    # 连接到SQLite数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_score_pk.db")
    logger.info(f"连接到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"数据库中的表: {tables}")
        
        # 查询scores表结构
        try:
            cursor.execute("PRAGMA table_info(scores);")
            columns = cursor.fetchall()
            logger.info(f"scores表结构: {columns}")
        except Exception as e:
            logger.error(f"查询scores表结构失败: {e}")
        
        # 查询所有记录
        try:
            cursor.execute("SELECT score_id, user_id, image_url, face_score FROM scores ORDER BY face_score DESC;")
            records = cursor.fetchall()
            logger.info(f"数据库中共有 {len(records)} 条记录")
            
            # 打印前10条记录
            for i, (score_id, user_id, image_url, face_score) in enumerate(records[:10]):
                logger.info(f"记录 {i+1}: ID={score_id}, 用户ID={user_id}, 图片URL={image_url}, 分数={face_score}")
            
            # 检查重复URL
            cursor.execute("""
                SELECT image_url, COUNT(*) as count
                FROM scores
                GROUP BY image_url
                HAVING COUNT(*) > 1
                ORDER BY count DESC;
            """)
            duplicate_urls = cursor.fetchall()
            logger.info(f"找到 {len(duplicate_urls)} 组重复的image_url")
            
            for url, count in duplicate_urls[:5]:
                logger.info(f"重复URL: {url}, 出现 {count} 次")
                
            # 检查相似URL (不同文件名但可能是相同图片)
            similar_urls = []
            url_parts = {}
            
            for score_id, user_id, image_url, face_score in records:
                if image_url and '/uploads/' in image_url:
                    # 提取用户ID部分
                    parts = image_url.split('/')[-1].split('_')
                    if len(parts) > 1:
                        user_part = parts[0]
                        if user_part in url_parts:
                            url_parts[user_part].append((score_id, image_url, face_score))
                        else:
                            url_parts[user_part] = [(score_id, image_url, face_score)]
            
            # 检查每个用户是否有多张照片
            for user_part, urls in url_parts.items():
                if len(urls) > 1:
                    logger.info(f"用户 {user_part} 有 {len(urls)} 张照片")
                    for score_id, url, score in urls[:3]:  # 只显示前3张
                        logger.info(f"  ID={score_id}, URL={url}, 分数={score}")
            
        except Exception as e:
            logger.error(f"查询记录失败: {e}")
        
    except Exception as e:
        logger.error(f"显示数据库记录时出错: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def clean_duplicates_direct_sql():
    """使用直接SQL查询清理重复图片记录"""
    # 连接到SQLite数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_score_pk.db")
    logger.info(f"连接到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 查找所有重复的image_url
        logger.info("查找重复的image_url...")
        cursor.execute("""
            SELECT image_url, COUNT(*) as count
            FROM scores
            GROUP BY image_url
            HAVING COUNT(*) > 1
        """)
        
        duplicate_urls = cursor.fetchall()
        logger.info(f"找到 {len(duplicate_urls)} 组重复的image_url")
        
        total_deleted = 0
        
        # 2. 对于每组重复的URL，只保留分数最高的记录
        for url, count in duplicate_urls:
            logger.info(f"处理重复URL: {url}, 共 {count} 条记录")
            
            # 查找该URL对应的所有记录
            cursor.execute("""
                SELECT score_id, face_score
                FROM scores
                WHERE image_url = ?
                ORDER BY face_score DESC
            """, (url,))
            
            records = cursor.fetchall()
            if not records:
                continue
                
            # 保留第一条（分数最高的）记录，删除其他记录
            highest_score_id = records[0][0]
            highest_score = records[0][1]
            
            for score_id, score in records[1:]:
                logger.info(f"删除重复记录: ID={score_id}, URL={url}, 分数={score}, 保留ID={highest_score_id}, 分数={highest_score}")
                cursor.execute("DELETE FROM scores WHERE score_id = ?", (score_id,))
                total_deleted += 1
        
        # 提交更改
        conn.commit()
        logger.info(f"总共删除了 {total_deleted} 条重复记录")
        
    except Exception as e:
        logger.error(f"清理过程中出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("开始清理重复图片记录...")
    show_database_records()
    clean_duplicates_direct_sql()
    logger.info("清理完成") 