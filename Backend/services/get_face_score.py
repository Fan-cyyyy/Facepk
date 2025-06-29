import requests
import base64
from pprint import pprint

def get_access_token(api_key, secret_key):
    token_url = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    response = requests.post(token_url, params=params).json()
    return response.get('access_token')

def main():
    api_key = 'eb8uJZjrOrLwa5acw59JbxGw'
    secret_key = 'X5YB0qlJuZjyCEKHPhFEQs0RJWitWbj7'

    # 获取 access_token
    access_token = get_access_token(api_key, secret_key)
    print("Access Token:", access_token)

    # 图片路径
    # img_path = r'C:\Users\Fancy\Pictures\b_582b0f1421822f9fcdce582e7dc77e8c.jpg'
    img_path = r"C:\Users\Fancy\Pictures\OIP-C.webp"
    # 读取并转为 base64 字符串
    with open(img_path, "rb") as image_file:
        image_base64_str = base64.b64encode(image_file.read()).decode("utf-8")

    # 调用人脸检测接口（v3）
    detect_url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={access_token}"

    payload = {
        "image": image_base64_str,
        "image_type": "BASE64",
        "face_field": "age,gender,beauty,expression,face_shape,landmark"
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(detect_url, headers=headers, json=payload)
    pprint(response.json())
    data = response.json()
    face = data['result']['face_list'][0]
    print(face['beauty'])

if __name__ == '__main__':
    main()