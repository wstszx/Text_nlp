import pandas as pd
import requests
import concurrent.futures
import os

os.environ['PYTHONBUFFERED'] = '1'

# 读取excel文件
df = pd.read_excel("D:\\doc\\其它\\chatgpt_app_statistics.xlsx", sheet_name='网页应用')

# 获取“网址”列
urls = df['网址']

def check_url(url):
    try:
        # 发送请求
        response = requests.get(url, timeout=5)
        # 打印每次读取的网址内容和请求状态码
        print(f"URL: {url}, Status Code: {response.status_code}")
        # 如果返回状态码不是200，删除这一行
        if response.status_code != 200:
            df.drop(df[df['网址'] == url].index, inplace=True)
    except:
        print(f"URL: {url}, 出现错误")
        # 如果请求出错，删除这一行
        df.drop(df[df['网址'] == url].index, inplace=True)

# 遍历每个网址
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(check_url, urls)

# 保存修改后的excel文件
df.to_excel('D:\\doc\\其它\\chatgpt_app_statistics_result.xlsx', index=False)


