import requests
import json
import re
import sys
import chardet
import pandas as pd
import os
import time
import numpy as np

MAX_TEXT_LENGTH = 1024
MAX_REQUESTS_PER_MINUTE = 50
BATCH_SIZE = 20  # 每次做多少行内容的文本分析

proxies = {
    'http': 'http://192.168.3.54:7890',
    'https': 'http://192.168.3.54:7890'
}

post_url = 'https://poe.com/api/gql_POST'


headers = {
    "authority": "poe.com",
    "method": "POST",
    "path": "/api/gql_POST",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "cookie": "p-b=UFmk_MUjNtIsbJccxsFfDg%3D%3D",
    "origin": "https://poe.com",
    "poe-formkey": "84573ebbfcdd3bcb825946a0d0919694",
    "poe-tag-id": "86d936dd3cd206fd1f1eec2bb226cb0f",
    "poe-tchannel": "poe-chan54-8888-iuoncfqcaztabrynlwlw",
    "referer": "https://poe.com/ChatGPT",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}


def get_sentiment(text, detect_type):
    if detect_type == 1:
        prompt = "分别判断以下每行文本是否为正能量，请仅回答 '正能量' 或 '负能量' 或 '中性':\n"
    elif detect_type == 2:
        prompt = "分别判断以下每行文本是否为不良信息，请仅回答 '正面' 或 '负面' 或 '中性':\n"
    prompt += text
    data = {
        "queryName": "chatHelpers_sendMessageMutation_Mutation",
        "variables": {
            "chatId": 10474918,
            "bot": "chinchilla",
            "query": prompt,
            "source": "null",
            "withChatBreak": "false",
            "clientNonce": "4LP0E9Hb7Jci4e9D"
        },
        "query": "mutation chatHelpers_sendMessageMutation_Mutation(\n  $chatId: BigInt!\n  $bot: String!\n  $query: String!\n  $source: MessageSource\n  $withChatBreak: Boolean!\n  $clientNonce: String\n) {\n  messageEdgeCreate(chatId: $chatId, bot: $bot, query: $query, source: $source, withChatBreak: $withChatBreak, clientNonce: $clientNonce) {\n    chatBreak {\n      cursor\n      node {\n        id\n        messageId\n        text\n        author\n        suggestedReplies\n        creationTime\n        state\n      }\n      id\n    }\n    message {\n      cursor\n      node {\n        id\n        messageId\n        text\n        author\n        suggestedReplies\n        creationTime\n        state\n        clientNonce\n        chat {\n          shouldShowDisclaimer\n          id\n        }\n      }\n      id\n    }\n  }\n}\n"
    }

    try:
        res = requests.post(post_url, headers=headers, data=json.dumps(
            data), proxies=proxies, verify=False)
        print("res.content.decode()==", res.content.decode())
        pattern = re.compile(r'"parts":\[(.*?)\]')
        matches = pattern.findall(res.content.decode())
        sentiment = matches[-1].strip('"')
        # # Update the headers with the new cookie value
        # new_cookie = res.cookies.get_dict()['cf_clearance']
        # headers['cookie'] = f"cf_clearance={new_cookie}"

        print(f"文本内容: {prompt}")
        print(f"文本分析结果: {sentiment}\n")
    except IndexError as e:
        sentiment = '没有找到情感分析结果'
        print(f"出现异常: {e}")
        # print(f"未找到以下文本的文本分析结果: {text}\n")
        print(f"文本内容: {prompt}")

    return sentiment, matches


# 读取命令行参数
detect_type = int(sys.argv[1])
excel_path = sys.argv[2]

# 读取 Excel 文件
file_ext = os.path.splitext(excel_path)[1]  # 获取文件后缀名
if file_ext == ".xlsx" or file_ext == ".xlsm":
    df = pd.read_excel(excel_path, header=0, engine="openpyxl")
elif file_ext == ".xls":
    df = pd.read_excel(excel_path, header=0, engine="xlrd")
elif file_ext == ".csv":
    # 使用 chardet 库自动检测文件编码格式
    with open(excel_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    # print("文件路径：", excel_path, "编码：", encoding)
    # 使用 pandas 读取 csv 文件
    df = pd.read_csv(excel_path, header=0, encoding=encoding)
else:
    print("不支持的文件格式")
    exit()

# 定义列来写入情感分析结果
sentiment_col = "检测结果"

num_rows = df.shape[0]
num_batches = num_rows // BATCH_SIZE + 1
for i in range(num_batches):
    start_idx = i * BATCH_SIZE
    end_idx = min((i + 1) * BATCH_SIZE, num_rows)
    batch_text = ''
    for j, (row_num, row) in enumerate(df.iloc[start_idx:end_idx].iterrows(), start=1):
        combined_text = " ".join(
            [str(row[col]) for col in df.columns if col != sentiment_col and not pd.isna(row[col])])
        batch_text += f"{j}. {combined_text}\n"
    sentiment, matches = get_sentiment(batch_text, detect_type)
    # print("拼接的内容：", batch_text)
    # print("文本分析结果：", sentiment)
    time.sleep(5)
    sentiment_list = re.findall(r'正面|负面|中性', sentiment)
    # print("matches==", len(matches))
    # print("sentiment==", sentiment)
    # print("sentiment_list==", sentiment_list)

    for j in range(len(sentiment_list)):
        if sentiment_list[j] != '':
            df.loc[start_idx + j, sentiment_col] = sentiment_list[j]


# 写入情感分析结果到Excel文件
if file_ext == ".xlsx" or file_ext == ".xls":
    with pd.ExcelWriter(excel_path) as writer:
        df.to_excel(writer, index=False, header=True)
elif file_ext == ".csv":
    df.to_csv(excel_path, index=False, header=True, encoding=encoding)

print("文本分析完成！请检查结果文件 '{}'。".format(excel_path))
