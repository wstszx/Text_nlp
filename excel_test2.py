# 导入所需的库
import openai
import pandas as pd

# 设置openai api密钥
openai.api_key = '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'

# 定义一个函数，用于对文本进行情感分析，并返回结果
def get_sentiments(texts):
    sentiments = []  # 创建一个空列表，用于存储每条文本的情感极性
    for text in texts:  # 遍历输入的文本列表
        prompt = f"判断下面内容是否为正能量,返回'正能量'或'负能量':\n{text}\n正能量极性:",
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=prompt,
            temperature=0, # 这个参数决定了生成文本时模型采用多大程度的随机性和多样性。温度越高，生成文本越不确定、越有创意、越可能出现意外或者错误；温度越低，生成文本越确定、越保守、越可能重复或者无聊。你可以根据你想要得到什么样风格和质量的文本来调整这个参数。
            max_tokens=100,
            top_p=1,#这个参数决定了生成文本时模型采用nucleus sampling策略的概率阈值。nucleus sampling策略是指模型只从概率最高的一部分候选令牌中选择一个令牌，而不是从所有候选令牌中选择。top_p的值越大，表示选择范围越广，生成文本越多样；top_p的值越小，表示选择范围越窄，生成文本越确定。
            frequency_penalty=0,#这个参数决定了生成文本时对重复令牌进行惩罚的系数。重复令牌是指在生成文本中已经出现过的令牌。frequency_penalty的值越大，表示对重复令牌的惩罚越大，生成文本越避免重复；frequency_penalty的值越小，表示对重复令牌的惩罚越小，生成文本越可能重复。你可以根据你想要得到什么样原创性和连贯性的文本来调整这个参数。
            presence_penalty=0,#这个参数决定了生成文本时对已出现令牌进行惩罚的系数。已出现令牌是指在输入文本或者上下文中已经出现过的令牌。presence_penalty的值越大，表示对已出现令牌的惩罚越大，生成文本越避免使用相同或者相关的内容
        )
        sentiment = response['choices'][0]['text']
        sentiments.append(sentiment)  # 将情感极性添加到列表中
    return sentiments


# 读取excel文件中的第一列前10条文本，并存储在一个列表中
df = pd.read_excel("D:\\doc\\信通院二期训练文本数据\\正能量测试.xlsx",
                   usecols=[0], header=None)
texts = df[0].tolist()
print('输入的文本', texts)

# 调用get_sentiments函数获取批量情感分析结果，并添加到df数据框中作为新的一列"Sentiment"
df[1] = get_sentiments(texts)

# 将df数据框写入一个新的的excel文件中，覆盖原有内容
df.to_excel('D:\\doc\\信通院二期训练文本数据\\正能量测试检测结果.xlsx', index=False, header=False)

# 打印每条文本的检测结果
for i in range(len(texts)):
    print(f"Text: {texts[i]}\nSentiment: {df[1][i]}\n")
