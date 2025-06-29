"""
百度AI API测试脚本
"""
import os
import sys
import base64
import requests
import json
from pprint import pprint
from pathlib import Path

# 获取百度AI API密钥
def load_config():
    """加载配置"""
    config = {}
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=', 1)
                config[key] = value
    return config

def get_access_token(api_key, secret_key):
    """获取百度AI访问令牌"""
    token_url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    response = requests.post(token_url, params=params).json()
    return response.get('access_token')

def detect_face(image_path, access_token):
    """检测人脸"""
    # 读取并转为base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    
    # 调用人脸检测接口V3
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
    return response.json()

def main():
    """主函数"""
    # 获取配置
    config = load_config()
    api_key = config.get('BAIDU_AI_API_KEY', 'eb8uJZjrOrLwa5acw59JbxGw')
    secret_key = config.get('BAIDU_AI_SECRET_KEY', 'X5YB0qlJuZjyCEKHPhFEQs0RJWitWbj7')
    
    # 获取access_token
    access_token = get_access_token(api_key, secret_key)
    print("Access Token:", access_token)
    
    # 测试图片路径，请修改为您的图片路径
    image_path = input("请输入图片路径(完整路径): ")
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        return
    
    # 检测人脸
    result = detect_face(image_path, access_token)
    
    # 显示结果
    pprint(result)
    
    # 如果成功，提取并显示beauty分数
    if result.get('error_code', -1) == 0 and result.get('result'):
        face_list = result['result'].get('face_list', [])
        if face_list:
            beauty = face_list[0].get('beauty', 0)
            print(f"\n颜值评分: {beauty}")
        else:
            print("未检测到人脸")
    else:
        print(f"检测失败: {result.get('error_msg', '未知错误')}")

if __name__ == "__main__":
    main() 