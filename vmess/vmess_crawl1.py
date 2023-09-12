# 导入所需的模块
import os
import re
import time
import yaml
import requests
import schedule
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from flask import Flask, send_file
app = Flask(__name__)

# 定义要访问的网页地址和要使用的Google Drive API范围
url = "https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 定义要使用的转换服务的地址和参数（这里以ClashToVmess为例）
convert_url = "https://vmess-to-clash.herokuapp.com/vmess"
convert_params = {"url": "", "type": "clash"}

def upload_clash():
    """将clash.yaml文件上传到google drive中"""
    # 尝试从token.json文件中获取凭据，如果没有或无效，则让用户登录并保存新的凭据
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "clash\credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # 创建一个drive服务对象并使用凭据进行授权
        service = build("drive", "v3", credentials=creds)
        # 使用MediaFileUpload类创建一个文件对象并指定文件名和MIME类型
        media = MediaFileUpload("clash.yaml", mimetype="text/plain")
        # 查询Google Drive中是否存在clash.yaml文件，并获取其id
        query = "name='clash.yaml' and trashed=false"
        response = service.files().list(q=query, spaces="drive").execute()
        files = response.get("files", [])
        if files:
            # 如果存在clash.yaml文件，则获取其id
            file_id = files[0].get("id")
            # 调用service.files().update()方法并传递文件id和文件对象
            file = service.files().update(fileId=file_id, media_body=media).execute()
            # 打印文件的id和名称
            print(f"Updated file {file.get('name')} with id {file.get('id')}")
        else:
            # 如果不存在clash.yaml文件，则创建一个新的文件
            file = service.files().create(
                body={"name": "clash.yaml"}, media_body=media
            ).execute()
            # 打印文件的id和名称
            print(f"Created file {file.get('name')} with id {file.get('id')}")
    except HttpError as error:
        # 处理来自drive API的错误。
        print(f"发生错误: {error}")


def get_and_write_clash():
    """从网页获取vmess链接并转成clash订阅内容，然后写入clash.yaml文件中"""
    # 发送请求并获取网页内容
    response = requests.get(url)
    content = response.text
    # 使用正则表达式匹配vmess链接
    pattern = r"vmess://([\s\S]*?)</p>"
    vmess_links = re.findall(pattern, content)
    # 取第一个vmess链接并打印
    vmess = "vmess://" + vmess_links[0]
    print(vmess)
    # 将vmess链接解码为json对象
    decodeVmessLink = base64.b64decode(vmess[8:])
    decodeVmessLink = json.loads(decodeVmessLink)
    # 读取模板yaml文件内容
    with open("vmess/template.yaml", encoding="utf-8-sig") as file:
        file_data = file.read()
    yamlObject = yaml.load(file_data, yaml.FullLoader) 
    # 修改yaml对象中的代理服务器信息
    proxies = yamlObject["proxies"][0]
    proxies["server"] = decodeVmessLink["add"]
    proxies["uuid"] = decodeVmessLink["id"]
    proxies["ws-opts"]["path"] = decodeVmessLink["path"]
    yamlObject["proxies"][0] = proxies
    # 将yaml对象转换为字符串并打印
    # clash = yaml.dump(yamlObject, encoding="utf-8-sig")
    print(proxies)
    # 将clash订阅内容写入clash.yaml文件中
    with open('clash.yaml', 'w', encoding='utf-8-sig') as file:
        yaml.dump(yamlObject, file, encoding="utf-8-sig")

def job():
    # 调用get_and_write_clash函数执行主要功能
    get_and_write_clash()
    # 调用upload_clash函数将clash.yaml文件上传到google drive中
    # upload_clash()


schedule.every(10).seconds.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Execution stopped by user")

@app.route('/api/clash')  
def get_clash():
    return send_file('clash.yaml')

if __name__ == '__main__':
    app.run()
