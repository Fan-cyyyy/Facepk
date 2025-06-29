#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通过比较图片内容来清理重复图片
对于相同分数的图片，计算图片哈希并比较，保留最新的一张
"""

import os
import sys
import logging
import sqlite3
import hashlib
from PIL import Image
import io
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_image_hash(image_path):
    """计算图片哈希值"""
    try:
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"计算图片哈希值失败: {e}")
        return None

def clean_duplicates_by_content():
    """通过比较图片内容清理重复图片"""
    # 连接到SQLite数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_score_pk.db")
    logger.info(f"连接到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 查找所有相同分数的记录
        logger.info("查找相同分数的记录...")
        cursor.execute("""
            SELECT face_score, COUNT(*) as count
            FROM scores
            GROUP BY face_score
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicate_scores = cursor.fetchall()
        logger.info(f"找到 {len(duplicate_scores)} 组相同分数的记录")
        
        total_deleted = 0
        
        # 2. 对于每组相同分数的记录，计算图片哈希值并比较
        for score, count in duplicate_scores:
            logger.info(f"处理分数 {score}, 共 {count} 条记录")
            
            # 查询该分数对应的所有记录
            cursor.execute("""
                SELECT score_id, user_id, image_url, scored_at
                FROM scores
                WHERE face_score = ?
            """, (score,))
            
            records = cursor.fetchall()
            
            # 计算每条记录的图片哈希值
            record_hashes = []
            for score_id, user_id, image_url, scored_at in records:
                if not image_url:
                    continue
                    
                # 构建完整路径
                image_path = image_url
                if image_path.startswith('/'):
                    image_path = image_path[1:]  # 去除开头的斜杠
                    
                # 尝试不同的路径组合
                full_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", image_path),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path),
                    os.path.join(os.getcwd(), image_path),
                    os.path.join(os.getcwd(), "..", image_path)
                ]
                
                image_hash = None
                for path in full_paths:
                    if os.path.exists(path):
                        image_hash = calculate_image_hash(path)
                        if image_hash:
                            break
                
                if image_hash:
                    # 将记录ID、哈希值和时间戳添加到列表
                    timestamp = 0
                    if scored_at:
                        try:
                            dt = datetime.fromisoformat(scored_at.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            pass
                    
                    record_hashes.append((score_id, image_hash, timestamp or 0, user_id, image_url))
                else:
                    logger.warning(f"无法计算图片哈希值: {image_url}")
            
            # 按哈希值分组
            hash_groups = {}
            for score_id, image_hash, timestamp, user_id, image_url in record_hashes:
                if image_hash in hash_groups:
                    hash_groups[image_hash].append((score_id, timestamp, user_id, image_url))
                else:
                    hash_groups[image_hash] = [(score_id, timestamp, user_id, image_url)]
            
            # 对于每组相同哈希值的记录，只保留最新的一条
            for image_hash, records in hash_groups.items():
                if len(records) > 1:
                    # 按时间戳排序，保留最新的
                    records.sort(key=lambda x: x[1], reverse=True)
                    keep_record = records[0]
                    
                    logger.info(f"保留记录: ID={keep_record[0]}, 用户ID={keep_record[2]}, URL={keep_record[3]}")
                    
                    # 删除其他记录
                    for score_id, timestamp, user_id, image_url in records[1:]:
                        logger.info(f"删除重复记录: ID={score_id}, 用户ID={user_id}, URL={image_url}")
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
    logger.info("开始通过图片内容清理重复图片...")
    clean_duplicates_by_content()
    logger.info("清理完成") 