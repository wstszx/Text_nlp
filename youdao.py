# 导入requests库和json库
import requests
import json

# 定义要翻译的内容
content = "我不愿意长大"

# 定义有道翻译的URL和表单数据
url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
data = {
    "i": content,
    "from": "AUTO",
    "to": "AUTO",
    "smartresult": "dict",
    "client": "fanyideskweb",
    "doctype": "json",
    "version": "2.1",
    # 这些参数可能需要根据有道翻译的加密规则进行修改
    "keyfrom": "fanyi.web",
    "action": "FY_BY_REALTlME",
    "salt": "16395686288167",
    "sign": "b4c0a7a4e0c8b9e6c2d5d7b9a1f8a9d6",
    "lts": "1639568628816",
    "bv": "b286f0a34340b928819a6f64492585e8"
}

# 发送POST请求，获取响应数据
response = requests.post(url, data=data)
# 将响应数据转换为JSON格式
json_data = response.json()
# 提取翻译结果
result = json_data["translateResult"][0][0]["tgt"]
# 打印翻译结果
print(result)