import requests
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flaresolverr import CloudflareSolver


get_url = 'https://freegpt.top/'
post_url = 'https://freegpt.top/backend-api/conversation'

headers = {
    "authority": "freegpt.top",
    "method": "POST",
    "path": "/backend-api/conversation",
    "scheme": "https",
    "accept": "text/event-stream",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer",
    "content-type": "application/json",
    "origin": "https://freegpt.top",
    "referer": "https://freegpt.top/",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

def get_cf_clearance():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.add_argument('--output=/dev/null')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(options=options)
    driver.get(get_url)

    # Wait for the JavaScript challenge to be solved using FlareSolverr
    solver = CloudflareSolver("http://localhost:8191")
    solver.solve(driver.current_url)
    time.sleep(5)

    # Retrieve all cookies
    cookies = driver.get_cookies()
    print(cookies)

    # Find the cf_clearance cookie
    cf_clearance_cookie = None
    for cookie in cookies:
        if cookie['name'] == 'cf_clearance':
            cf_clearance_cookie = cookie['value']
            break

    driver.quit()

    return cf_clearance_cookie


def main():
    cf_clearance_cookie = get_cf_clearance()
    if not cf_clearance_cookie:
        raise Exception("Unable to retrieve cf_clearance cookie")

    headers['cookie'] = f'cf_clearance={cf_clearance_cookie}'

    while True:
        try:
            question = input("请输入你想问的问题：")
            data = {
                "action": "next",
                "messages": [
                    {
                        "id": "04464795-c749-4742-b202-48b2994d481fa",
                        "role": "user",
                        "content": {
                            "content_type": "text",
                            "parts": [question]
                        }
                    }
                ],
                "parent_message_id": "d720d2c8-e46c-4495-84ae-58d3ae1c9eeb",
                "model": "text-davinci-002-render"
            }

            res = requests.post(post_url, headers=headers, data=json.dumps(data))

            pattern = re.compile(r'"parts":\[(.*?)\]')
            matches = pattern.findall(res.content.decode())
            last_part = matches[-1]
            print(last_part)

        except KeyboardInterrupt:
            print("退出聊天")
            break
        except Exception as e:
            print(f"出现错误：{e}")


if __name__ == '__main__':
    main()