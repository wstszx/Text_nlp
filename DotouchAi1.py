import requests
import json
from datetime import datetime
import pandas as pd

url = "http://ai.dotouch.top/api/v1/chat/completions"

headers = {
    'Host': 'ai.dotouch.top',
    'Proxy-Connection': 'keep-alive',
    'accept': 'text/event-stream',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.119 Safari/537.36 Language/zh wxwork/4.1.26 (MicroMessenger/6.2) WindowsWechat MailPlugin_Electron WeMail embeddisk',
    'Content-Type': 'application/json',
    'Origin': 'http://ai.dotouch.top',
    'Referer': 'http://ai.dotouch.top/chat/share?shareId=hldolev0ln684zk4lihuhqt5&chatId=dla88rwvc1kh',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

now = datetime.now()
cTime = now.strftime("%Y-%m-%d %H:%M:%S %A")

excel_file = r"D:\doc\其它\触点ai问答.xlsx"
df = pd.read_excel(excel_file)

answers = []

for index, row in df.iterrows():
    question = row['问题']

    data = {
        "messages": [
            {
                "dataId": "ltHHhwnbLwqYkHNjc1YhYQU8",
                "role": "user",
                "content": question
            }
        ],
        "variables": {
            "name": "杨驰",
            "cTime": cTime
        },
        "shareId": "hldolev0ln684zk4lihuhqt5",
        "chatId": "dla88rwvc1kh",
        "outLinkUid": "shareChat-1718602673987-lIkRwlxKwZrUdK0JQmydxyTB",
        "detail": True,
        "stream": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = json.loads(response.text)

    print(f"问题: {question}")
    # print(f"Response Text: {response.text}")
    content = response_data['choices'][0]['message']['content']
    print(f"回答 : {content}")

    answers.append(content)
    # print(f"Merged Answer: {content}")

df['回答'] = answers
df['提问者'] = '杨驰'

df.to_excel(excel_file, index=False)
