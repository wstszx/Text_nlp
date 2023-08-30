import schedule
import requests
import re
import pyperclip
import pyautogui
import time

url = 'https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7'

def import_vmess(vmess):
    # 复制vmess链接到剪贴板
    pyperclip.copy(vmess)
    # 打开v2rayN软件
    pyautogui.hotkey('win', 'r') # 按下win+r键打开运行窗口
    time.sleep(1) # 等待1秒
    pyautogui.typewrite('v2rayN.exe') # 输入v2rayN.exe
    pyautogui.press('enter') # 按下回车键
    time.sleep(5) # 等待5秒，等待软件启动
    # 导入vmess链接
    pyautogui.hotkey('ctrl', 'i') # 按下ctrl+i键打开导入窗口
    time.sleep(1) # 等待1秒
    pyautogui.press('enter') # 按下回车键选择从剪贴板导入
    time.sleep(1) # 等待1秒
    pyautogui.press('enter') # 按下回车键确认导入
    time.sleep(1) # 等待1秒
    pyautogui.press('esc') # 按下esc键关闭导入窗口

def get_and_import_vmess():
    response = requests.get(url)
    content = response.text
    pattern = r'vmess://([\s\S]*?)</p>'
    vmess_links = re.findall(pattern, content)
    vmess = "vmess://" + vmess_links[0]
    print(vmess)
    import_vmess(vmess)

# 安排每隔3小时运行一次get_and_import_vmess函数
schedule.every(3).hours.do(get_and_import_vmess)

# 无限循环，等待任务执行
while True:
    schedule.run_pending()
    time.sleep(1)
