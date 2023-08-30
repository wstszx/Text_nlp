import requests
import json

proxies = {
    'http': 'http://192.168.3.54:7890',
    'https': 'http://192.168.3.54:7890'
}

post_url = 'https://freegpt.top/backend-api/conversation'

# headers = {
#     "authority": "freegpt.top",
#     "method": "POST",
#     "path": "/backend-api/conversation",
#     "scheme": "https",
#     "accept": "*/*",
#     "accept-encoding": "gzip, deflate, br",
#     "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
#     "authorization": "Bearer",
#     "content-length": "55",
#     "content-type": "application/json",
#     "cookie": "cf_clearance=vmPbFWQlabij.TzT8Dch1_ekNtZVqp5axZY76DaxjGY-1681718602-0-250",
#     "origin": "https://freegpt.top",
#     "referer": "https://freegpt.top/",
#     "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
#     "sec-ch-ua-mobile": "?1",
#     "sec-ch-ua-platform": "Android",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-origin",
#     "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
# }

headers = {
    "authority": "freegpt.top",
    "method": "POST",
    "path": "/backend-api/conversation",
    "scheme": "https",
    "accept": "text/event-stream",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer",
    "content-length": "236",
    "content-type": "application/json",
    "cookie": "cf_clearance=5sOsBL4hlgWxQm_MA7rXxEHSVi947WFhKKqwpKxck2M-1681727576-0-250",
    "origin": "https://freegpt.top",
    "referer": "https://freegpt.top/",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
    
}


# data = {
#     "input": "你好",
#     "model": "text-moderation-playground"
# }

data = {
    "action": "next",
    "messages": [
        {
            "id": "da028d47-fe69-44f5-8806-cff808de2450",
            "role": "user",
            "content": {
                "content_type": "text",
                "parts": [
                    "你好"
                ]
            }
        }
    ],
    "parent_message_id": "4461504f-759c-4f31-b378-d3106e8791e2",
    "model": "text-davinci-002-render"
}

res = requests.post(post_url, headers=headers, data=json.dumps(
    data), proxies=proxies, verify=False)
print(res.text)
