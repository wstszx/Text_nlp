import openai
import pandas as pd
import sys

# 设置OpenAI API密钥
openai.api_key = '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'

# 定义一个函数，用于对文本进行情感分析，并返回结果
def get_sentiment(text, detect_type):
    
    if detect_type == 1:
        prompt = f"判断下面内容是否为正能量,返回'正能量'或'负能量':\n{text}\n正能量极性:"
    elif detect_type == 2:
        prompt = f"判断下面内容是否为不良信息,返回'是'或'否':\n{text}\n是否是不良信息:"

    # 调用OpenAI API进行文本生成，生成一个极性，此处采用text-davinci-003模型
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # 打印生成的情感极性并返回
    sentiment = response['choices'][0]['text'].strip()
    return sentiment

# 读取命令行参数，detect_type为1时表示正能量检测，为2时表示不良信息检测，excel_path为要处理的Excel文件的路径
detect_type = int(sys.argv[1])
excel_path = sys.argv[2]

# 读取输入的Excel文件，并将每一行的前几列（去掉空值）拼接为一段文本
df = pd.read_excel(excel_path)

#获取输入文件列数,从最后一列开始，查找每行最后一个非空单元格的列号
col_num = df.shape[1]
for i in range(df.shape[0]):
    for j in range(df.shape[1]-1, -1, -1):
        if pd.notna(df.iloc[i, j]):
            col_num = j
            break

# 批量进行情感分析，将结果保存在df的新列"Sentiment"中
df['Sentiment'] = [get_sentiment(text, detect_type) for text in df.iloc[:, :col_num + 1].apply(lambda x: '\n'.join(x.dropna().astype(str)), axis=1).tolist()]

# 将结果写入输出的Excel文件中，覆盖原有数据
with pd.ExcelWriter(excel_path) as writer:
    df.to_excel(writer, index=False)