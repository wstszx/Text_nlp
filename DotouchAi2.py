import requests
import json
from datetime import datetime
import pandas as pd
import threading
import os
import google.generativeai as genai

name = "杨驰"

def send_request(row):
    question = row['问题']
    data = {
        "messages": [
            {
                "dataId": "lMq4sp3RtCUPYi5JdJBHy6o5",  # 这里需要根据实际的 dataId 修改
                "role": "user",
                "content": question
            }
        ],
        "variables": {
            "name": name,
            "cTime": cTime
        },
        "shareId": "hldolev0ln684zk4lihuhqt5",  # 这里需要根据实际的 shareId 修改
        "chatId": "mn4abpz13v68",  # 这里需要根据实际的 chatId 修改
        "outLinkUid": "shareChat-1718602673987-lIkRwlxKwZrUdK0JQmydxyTB",  # 这里需要根据实际的 outLinkUid 修改
        "detail": True,
        "stream": False
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("API Response:", response.text) 
    response_data = json.loads(response.text)

    # Check if 'choices' key exists
    if 'choices' in response_data:
        content = response_data['choices'][0]['message']['content']
    else:
        print("Error: 'choices' key not found in response data.")
        return None, "Evaluation Failed"

    combined_text = f"问题: {question}\n回答: {content}"

    try:
        os.environ['http_proxy'] = 'http://127.0.0.1:7899'
        os.environ['https_proxy'] = 'http://127.0.0.1:7899'

        genai.configure(api_key="AIzaSyAvWLhW91SdD2-YMiJgfjVSI8J6oCVb9UI")  # 这里需要替换成你的 API 密钥

        generation_config = {
          "temperature": 1,
          "top_p": 0.95,
          "top_k": 64,
          "max_output_tokens": 8192,
        }

        model = genai.GenerativeModel(
          model_name="gemini-1.5-flash",
          generation_config=generation_config,
        )

        chat_session = model.start_chat(history=[])
        print("会话开始")

        response = chat_session.send_message(f"分析以下问题和回答，回答的是否准确，只能回答'点赞'或'点踩'如果回答'点踩'，请说明理由。\n{combined_text}")
        print(f"问题: {question}")
        print(f"回答 : {content}")
        print(f"Gemini 评价: {response.text}")

        evaluation = response.text.strip().lower()
        if '点赞' in evaluation:
            send_feedback(chat_item_id="lMq4sp3RtCUPYi5JdJBHy6o5", feedback_type="good", reason="")
        elif '点踩' in evaluation:
            reason = evaluation[3:].strip() 
            send_feedback(chat_item_id="lMq4sp3RtCUPYi5JdJBHy6o5", feedback_type="bad", reason=reason)
        else:
            evaluation = "评价失败"

        return content, evaluation
        
    except Exception as e:
        print("发生错误:", e)
        return content, "评价失败"

def send_feedback(chat_item_id, feedback_type, reason):
    """发送用户反馈信息"""
    feedback_url = "http://ai.dotouch.top/api/core/chat/feedback/updateUserFeedback"
    feedback_data = {
        "appId": "662f4907f0a297d9ede8a72c",
        "chatId": "mn4abpz13v68",  # 这里需要根据实际的 chatId 修改
        "chatItemId": chat_item_id,
        "shareId": "hldolev0ln684zk4lihuhqt5",  # 这里需要根据实际的 shareId 修改
        "outLinkUid": "shareChat-1718602673987-lIkRwlxKwZrUdK0JQmydxyTB",  # 这里需要根据实际的 outLinkUid 修改
    }
    if feedback_type == "good":
        feedback_data["userGoodFeedback"] = "yes"
    elif feedback_type == "bad":
        feedback_data["userBadFeedback"] = reason

    print(f"反馈：{feedback_data}")
    response = requests.post(feedback_url, headers=headers, data=json.dumps(feedback_data))
    print(f"反馈发送状态: {response.text}")


url = "http://ai.dotouch.top/api/v1/chat/completions"
headers = {
    'Host': 'ai.dotouch.top',
    'Proxy-Connection': 'keep-alive',
    'accept': 'text/event-stream',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.119 Safari/537.36 Language/zh wxwork/4.1.26 (MicroMessenger/6.2) WindowsWechat MailPlugin_Electron WeMail embeddisk',
    'Content-Type': 'application/json',
    'Origin': 'http://ai.dotouch.top',
    'Referer': 'http://ai.dotouch.top/chat/share?shareId=hldolev0ln684zk4lihuhqt5&chatId=mn4abpz13v68',  # 这里需要根据实际的 chatId 修改
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

now = datetime.now()
cTime = now.strftime("%Y-%m-%d %H:%M:%S %A")

excel_file = r"D:\doc\其它\触点ai问答.xlsx"
df = pd.read_excel(excel_file)

lock = threading.Lock()

answers = []
evaluations = []

threads = []
for index, row in df.iterrows():
    thread = threading.Thread(target=lambda q=row: (answers.append(send_request(q)[0]), evaluations.append(send_request(q)[1])))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

lock.acquire()
df['回答'] = answers
df['评价'] = evaluations
df['提问者'] = name
lock.release()

df.to_excel(excel_file, index=False)