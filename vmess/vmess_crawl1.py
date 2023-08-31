# 导入所需的模块
import schedule
import requests
import re
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import os

os.environ['HTTP_PROXY'] = 'http://192.168.3.54:7890'
os.environ['HTTPS_PROXY'] = 'http://192.168.3.54:7890'

# 定义要访问的网页地址和要使用的Google Drive API范围
url = 'https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def upload_vmess():
    """将vmess.txt文件上传到google drive中"""
    # 尝试从token.json文件中获取凭据，如果没有或无效，则让用户登录并保存新的凭据
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'vmess\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # 创建一个drive服务对象并使用凭据进行授权
        service = build('drive', 'v3', credentials=creds)
        # 使用MediaFileUpload类创建一个文件对象并指定文件名和MIME类型
        media = MediaFileUpload('vmess.txt', mimetype='text/plain')
        # 调用service.files().create()方法并传递文件对象
        file = service.files().create(body={'name': 'vmess.txt'}, media_body=media).execute()
        # 打印文件的id和名称
        print(f"Uploaded file {file.get('name')} with id {file.get('id')}")
    except HttpError as error:
        # 处理来自drive API的错误。
        print(f'发生错误: {error}')

def get_and_write_vmess():
    """从网页获取vmess链接并写入vmess.txt文件中"""
    # 发送请求并获取网页内容
    response = requests.get(url)
    content = response.text
    # 使用正则表达式匹配vmess链接
    pattern = r'vmess://([\s\S]*?)</p>'
    vmess_links = re.findall(pattern, content)
    # 取第一个vmess链接并打印
    vmess = "vmess://" + vmess_links[0]
    print(vmess)
    # 将vmess链接写入vmess.txt文件中
    with open('vmess.txt', 'w') as f:
        f.write(vmess)

# 调用get_and_write_vmess函数执行主要功能
get_and_write_vmess()
# 调用upload_vmess函数将vmess.txt文件上传到google drive中
upload_vmess()
