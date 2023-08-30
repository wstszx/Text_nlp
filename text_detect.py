import openai
import pandas as pd
import sys
import time
import os
import chardet

os.environ["http_proxy"] = "http://192.168.3.54:7890"
os.environ["https_proxy"] = "http://192.168.3.54:7890"

# 常量
MAX_TEXT_LENGTH = 1024
MAX_REQUESTS_PER_MINUTE = 50   # Modified maximum API requests per minute

# Set OpenAI API key
openai.api_key = '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'

# 定义函数对给定的文本执行情感分析并返回结果


def get_sentiment(text, detect_type):
    if detect_type == 1:
        prompt = "判断以下文本是否为正能量，请回答 '正能量' 或 '负能量' 或 '中性':\n"
    elif detect_type == 2:
        prompt = "判断以下文本是否为不良信息，请回答 '正面' 或 '负面' 或 '中性':\n"
    prompt += text + '\n极性:'
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    try:
        sentiment = response.choices[0].text.strip()
        print(f"文本内容: {text}")
        print(f"情感分析结果: {sentiment}\n")
    except IndexError:
        sentiment = 'OpenAI API 没有找到情感分析结果'
        print(f"未找到以下文本的情感分析结果: {text}\n")

    return sentiment


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
    df = pd.read_csv(excel_path,header=0, encoding=encoding)
else:
    print("不支持的文件格式")
    exit()

# 定义列来写入情感分析结果
sentiment_col = "检测结果"

# 清空并初始化计数器
api_requests_count = 0
loop_iteration = 0

# 迭代所有条目并对其进行情感分析
for row_num, row in df.iterrows():
    combined_text = " ".join(
        [str(row[col]) for col in df.columns if col != sentiment_col and not pd.isna(row[col])])
    if len(combined_text) > MAX_TEXT_LENGTH:
        subtexts = [combined_text[i:i+MAX_TEXT_LENGTH]
                    for i in range(0, len(combined_text), MAX_TEXT_LENGTH)]
        for subtext in subtexts:
            api_requests_count += 1
            if api_requests_count > MAX_REQUESTS_PER_MINUTE:
                # 如果 API 请求次数超过 MAX_REQUESTS_PER_MINUTE，请在5秒后重置计数器并等待
                api_requests_count = 0
                loop_iteration += 1
                if loop_iteration % 10 == 0:
                    print("已完成", loop_iteration, "次迭代。")
                time.sleep(5)
            sentiment = get_sentiment(subtext.strip(), detect_type)
            df.loc[row_num, sentiment_col] = sentiment
    else:
        api_requests_count += 1
        if api_requests_count > MAX_REQUESTS_PER_MINUTE:
            api_requests_count = 0
            loop_iteration += 1
            if loop_iteration % 10 == 0:
                print("已完成", loop_iteration, "次迭代。")
            time.sleep(5)
        sentiment = get_sentiment(combined_text.strip(), detect_type)
        df.loc[row_num, sentiment_col] = sentiment

# 写入情感分析结果到Excel文件
if file_ext == ".xlsx" or file_ext == ".xls":
    with pd.ExcelWriter(excel_path) as writer:
        df.to_excel(writer, index=False, header=True)
elif file_ext == ".csv":
    df.to_csv(excel_path, index=False, header=True, encoding=encoding)

print("文本分析完成！请检查结果文件 '{}'。".format(excel_path))
