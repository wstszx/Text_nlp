import requests

url = "https://api.siliconflow.cn/v1/chat/completions"

payload = {
    "model": "Qwen/Qwen2-7B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": "你是谁呀"
        }
    ],
    "max_tokens": 4096
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer sk-klawqyoodcrpleslhlotszwsqwvqsuugwxgozemrxiaeadmm"
}

def continue_conversation(user_message):
    payload["messages"].append({"role": "user", "content": user_message})
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

conversation_turns = []
while True:
    user_input = input("请输入你的消息：")
    if user_input.lower() == "结束对话":
        break
    response_json = continue_conversation(user_input)
    print("机器人回复：", response_json.get('choices', [{}])[0].get('message', {}).get('content', ''))
    conversation_turns.append((user_input, response_json.get('choices', [{}])[0].get('message', {}).get('content', '')))

print("对话结束。以下是完整对话记录：")
for turn in conversation_turns:
    print(turn)