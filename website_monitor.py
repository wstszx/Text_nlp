import requests
from bs4 import BeautifulSoup
import time
import hashlib

def get_element(url, css_selector):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.select_one(css_selector)
    return element

def monitor_element(url, css_selector, check_interval):
    print(f"开始监控：{url}")
    print(f"元素选择器：{css_selector}")

    last_element = None
    last_hash = None

    while True:
        try:
            current_element = get_element(url, css_selector)
            current_hash = hashlib.md5(str(current_element).encode('utf-8')).hexdigest()

            if last_element and current_hash != last_hash:
                print(f"元素发生变化：{current_element}")
                last_element = current_element
                last_hash = current_hash
            elif not last_element:
                last_element = current_element
                last_hash = current_hash

            time.sleep(check_interval)

        except Exception as e:
            print(f"发生错误：{e}")
            time.sleep(check_interval)

if __name__ == "__main__":
    url = "https://example.com"  # 替换为您想要监控的网址
    css_selector = "#element_id"  # 替换为您想要监控的元素的CSS选择器
    check_interval = 60  # 检查间隔（单位：秒）

    monitor_element(url, css_selector, check_interval)