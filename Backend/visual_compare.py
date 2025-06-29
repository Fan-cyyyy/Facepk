#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用更高级的图像相似度比较方法来检测和删除相似图片
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
from pathlib import Path
import base64

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到控制台
        logging.FileHandler('visual_compare.log')  # 同时保存到文件
    ]
)
logger = logging.getLogger(__name__)

def get_image_paths(image_url):
    """获取图片的可能路径"""
    if not image_url:
        return []
        
    # 构建完整路径
    image_path = image_url
    if image_path.startswith('/'):
        image_path = image_path[1:]  # 去除开头的斜杠
        
    # 尝试不同的路径组合
    return [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", image_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path),
        os.path.join(os.getcwd(), image_path),
        os.path.join(os.getcwd(), "..", image_path)
    ]

def load_image(image_path):
    """加载图片为PIL Image对象"""
    try:
        return Image.open(image_path)
    except Exception as e:
        logger.error(f"加载图片失败: {e}")
        return None

def calculate_image_similarity(img1_path, img2_path):
    """计算两张图片的相似度"""
    try:
        # 加载两张图片
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)
        
        if not img1 or not img2:
            return 0
        
        # 调整大小为相同尺寸
        size = (100, 100)  # 使用较小的尺寸加快比较速度
        img1 = img1.resize(size)
        img2 = img2.resize(size)
        
        # 转换为灰度图
        img1 = img1.convert('L')
        img2 = img2.convert('L')
        
        # 转换为numpy数组
        arr1 = np.array(img1).flatten()
        arr2 = np.array(img2).flatten()
        
        # 计算欧氏距离
        dist = np.sqrt(np.sum((arr1 - arr2) ** 2))
        max_dist = np.sqrt(size[0] * size[1] * 255 * 255)  # 最大可能距离
        
        # 转换为相似度（0-1之间）
        similarity = 1 - (dist / max_dist)
        
        return similarity
    except Exception as e:
        logger.error(f"计算图片相似度失败: {e}")
        return 0

def find_similar_images():
    """查找相似图片"""
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
        
        # 2. 加载所有图片
        print("加载所有图片...")
        logger.info("加载所有图片...")
        
        valid_records = []
        for score_id, user_id, image_url, face_score, scored_at in records:
            image_paths = get_image_paths(image_url)
            valid_path = None
            
            for path in image_paths:
                if os.path.exists(path):
                    valid_path = path
                    break
            
            if valid_path:
                print(f"找到有效图片路径: {valid_path}")
                valid_records.append((score_id, user_id, image_url, face_score, scored_at, valid_path))
            else:
                print(f"警告: 找不到图片: {image_url}")
                logger.warning(f"找不到图片: {image_url}")
        
        # 3. 计算图片相似度矩阵
        print("计算图片相似度矩阵...")
        logger.info("计算图片相似度矩阵...")
        
        similar_groups = []
        processed = set()
        
        for i, (id1, user1, url1, score1, time1, path1) in enumerate(valid_records):
            if id1 in processed:
                continue
                
            current_group = [(id1, user1, url1, score1, time1, path1)]
            
            for j, (id2, user2, url2, score2, time2, path2) in enumerate(valid_records):
                if i == j or id2 in processed:
                    continue
                    
                # 计算相似度
                similarity = calculate_image_similarity(path1, path2)
                print(f"图片 {id1} 和 {id2} 的相似度: {similarity:.4f}")
                
                # 相似度阈值，可以根据需要调整
                if similarity > 0.85:  # 85%相似度被认为是同一张图片
                    current_group.append((id2, user2, url2, score2, time2, path2))
                    processed.add(id2)
            
            if len(current_group) > 1:
                similar_groups.append(current_group)
                processed.add(id1)
        
        # 4. 处理相似图片组
        total_deleted = 0
        
        for group in similar_groups:
            print(f"发现 {len(group)} 张相似图片:")
            logger.info(f"发现 {len(group)} 张相似图片:")
            
            # 按分数排序，保留分数最高的
            group.sort(key=lambda x: x[3], reverse=True)
            keep_record = group[0]
            
            print(f"保留记录: ID={keep_record[0]}, 用户ID={keep_record[1]}, URL={keep_record[2]}, 分数={keep_record[3]}")
            logger.info(f"保留记录: ID={keep_record[0]}, 用户ID={keep_record[1]}, URL={keep_record[2]}, 分数={keep_record[3]}")
            
            # 删除其他记录
            for score_id, user_id, image_url, face_score, scored_at, _ in group[1:]:
                print(f"删除相似记录: ID={score_id}, 用户ID={user_id}, URL={image_url}, 分数={face_score}")
                logger.info(f"删除相似记录: ID={score_id}, 用户ID={user_id}, URL={image_url}, 分数={face_score}")
                cursor.execute("DELETE FROM scores WHERE score_id = ?", (score_id,))
                total_deleted += 1
        
        # 5. 提交更改
        conn.commit()
        print(f"总共删除了 {total_deleted} 条相似记录")
        logger.info(f"总共删除了 {total_deleted} 条相似记录")
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        logger.error(f"处理过程中出错: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始查找相似图片...")
    logger.info("开始查找相似图片...")
    find_similar_images()
    print("处理完成")
    logger.info("处理完成") 