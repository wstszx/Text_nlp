import schedule
import requests
import re
import pyperclip
import pyautogui
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

url = 'https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7'

def import_vmess(vmess):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    file = drive.CreateFile({'title': 'vmess.txt'})
    file.SetContentString(vmess)
    file.Upload()

def get_and_import_vmess():
    response = requests.get(url)
    content = response.text
    pattern = r'vmess://([\s\S]*?)</p>'
    vmess_links = re.findall(pattern, content)
    vmess = "vmess://" + vmess_links[0]
    print(vmess)
    import_vmess(vmess)

get_and_import_vmess()

# 安排每隔3小时运行一次get_and_import_vmess函数
# schedule.every(3).hours.do(get_and_import_vmess)

# 无限循环，等待任务执行
# while True:
#     schedule.run_pending()
#     time.sleep(1)
