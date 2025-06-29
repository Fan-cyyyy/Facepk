#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全面清理重复图片
比较所有照片的内容，无论分数是否相同，都检测并删除重复照片
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
import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV (cv2) 未安装，将使用简单哈希比较")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到控制台
        logging.FileHandler('duplicate_cleanup.log')  # 同时保存到文件
    ]
)
logger = logging.getLogger(__name__)

def calculate_image_hash(image_path):
    """计算图片哈希值"""
    try:
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"计算图片哈希值失败: {e}")
        return None

def calculate_perceptual_hash(image_path):
    """计算图片感知哈希值（更能检测相似但非完全相同的图片）"""
    if not CV2_AVAILABLE:
        return calculate_image_hash(image_path)
    
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return calculate_image_hash(image_path)
            
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
        return calculate_image_hash(image_path)

def clean_all_duplicates():
    """清理所有重复图片"""
    # 连接到SQLite数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_score_pk.db")
    print(f"连接到数据库: {db_path}")
    logger.info(f"连接到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 查询所有记录
        print("查询所有照片记录...")
        logger.info("查询所有照片记录...")
        cursor.execute("""
            SELECT score_id, user_id, image_url, face_score, scored_at
            FROM scores
            ORDER BY face_score DESC
        """)
        
        records = cursor.fetchall()
        print(f"数据库中共有 {len(records)} 条记录")
        logger.info(f"数据库中共有 {len(records)} 条记录")
        
        # 2. 计算所有照片的哈希值
        print("计算所有照片的哈希值...")
        logger.info("计算所有照片的哈希值...")
        record_hashes = []
        
        for score_id, user_id, image_url, face_score, scored_at in records:
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
                    print(f"计算图片哈希值: {path}")
                    # 使用感知哈希
                    image_hash = calculate_perceptual_hash(path)
                    if image_hash:
                        print(f"图片 {image_url} 的哈希值: {image_hash}")
                        break
            
            if image_hash:
                # 将记录信息添加到列表
                timestamp = 0
                if scored_at:
                    try:
                        dt = datetime.fromisoformat(scored_at.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                    except:
                        pass
                
                record_hashes.append((score_id, image_hash, timestamp or 0, user_id, image_url, face_score))
            else:
                print(f"警告: 无法计算图片哈希值: {image_url}")
                logger.warning(f"无法计算图片哈希值: {image_url}")
        
        # 3. 按哈希值分组
        hash_groups = {}
        for score_id, image_hash, timestamp, user_id, image_url, face_score in record_hashes:
            if image_hash in hash_groups:
                hash_groups[image_hash].append((score_id, timestamp, user_id, image_url, face_score))
            else:
                hash_groups[image_hash] = [(score_id, timestamp, user_id, image_url, face_score)]
        
        # 4. 处理重复记录
        total_deleted = 0
        
        for image_hash, records in hash_groups.items():
            if len(records) > 1:
                print(f"发现 {len(records)} 条哈希值为 {image_hash} 的重复记录")
                logger.info(f"发现 {len(records)} 条哈希值为 {image_hash} 的重复记录")
                
                # 按分数排序，保留分数最高的记录
                records.sort(key=lambda x: x[4], reverse=True)
                keep_record = records[0]
                
                print(f"保留记录: ID={keep_record[0]}, 用户ID={keep_record[2]}, URL={keep_record[3]}, 分数={keep_record[4]}")
                logger.info(f"保留记录: ID={keep_record[0]}, 用户ID={keep_record[2]}, URL={keep_record[3]}, 分数={keep_record[4]}")
                
                # 删除其他记录
                for score_id, timestamp, user_id, image_url, face_score in records[1:]:
                    print(f"删除重复记录: ID={score_id}, 用户ID={user_id}, URL={image_url}, 分数={face_score}")
                    logger.info(f"删除重复记录: ID={score_id}, 用户ID={user_id}, URL={image_url}, 分数={face_score}")
                    cursor.execute("DELETE FROM scores WHERE score_id = ?", (score_id,))
                    total_deleted += 1
        
        # 5. 提交更改
        conn.commit()
        print(f"总共删除了 {total_deleted} 条重复记录")
        logger.info(f"总共删除了 {total_deleted} 条重复记录")
        
        # 6. 更新图片哈希值到数据库
        print("更新图片哈希值到数据库...")
        logger.info("更新图片哈希值到数据库...")
        for score_id, image_hash, timestamp, user_id, image_url, face_score in record_hashes:
            cursor.execute("""
                UPDATE scores
                SET image_hash = ?
                WHERE score_id = ?
            """, (image_hash, score_id))
        
        conn.commit()
        print("图片哈希值更新完成")
        logger.info("图片哈希值更新完成")
        
    except Exception as e:
        print(f"清理过程中出错: {e}")
        logger.error(f"清理过程中出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始全面清理重复图片...")
    logger.info("开始全面清理重复图片...")
    clean_all_duplicates()
    print("清理完成")
    logger.info("清理完成") 