"""
EasyDL 文本分类单标签 调用模型公有云API Python3实现
"""

import json
import base64
import requests

"""
使用 requests 库发送请求
使用 pip（或者 pip3）检查我的 python3 环境是否安装了该库，执行命令
  pip freeze | grep requests
若返回值为空，则安装该库
  pip install requests
"""

# 目标文本的 本地文件路径，UTF-8编码，最大长度4096汉字
TEXT_FILEPATH = "D:/download/valid.txt"

# 可选的请求参数
# top_num: 返回的分类数量，不声明的话默认为 6 个
PARAMS = {"top_num": 2}

# 服务详情 中的 接口地址
MODEL_API_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/sentiment_cls/positive_energy"

# 替换成自己在百度AI平台中申请的API Key和Secret Key
API_KEY = "kpvEq5DAc7u0udcsIr0HRTnN"
SECRET_KEY = "iU2KwMuYx6EqLGGfsWXtdZCLVXNW2g8g"

print("1. 读取目标文本 '{}'".format(TEXT_FILEPATH))
with open(TEXT_FILEPATH, 'rb') as f:
    text_str = f.read()
print("将读取的文本填入 PARAMS 的 'text' 字段")
PARAMS["text"] = base64.b64encode(text_str).decode("utf-8")
print(text_str.decode())
print("2. 获取Access Token")
# 获取Access Token
host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}'
response = requests.get(host)
if response:
    # 解析返回的JSON数据，获取Access Token
    access_token = response.json().get('access_token')
    print(f'Access Token: {access_token}')
else:
    print('获取Access Token失败')
    exit()

print("3. 向模型接口 'MODEL_API_URL' 发送请求")
request_url = "{}?access_token={}".format(MODEL_API_URL, access_token)
response = requests.post(url=request_url, json=PARAMS)
response_json = response.json()
response_str = json.dumps(response_json, indent=4, ensure_ascii=False)
print("结果:{}".format(response_str))
