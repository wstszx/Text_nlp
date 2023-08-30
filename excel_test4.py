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
            # messages=[{"role": "system", "content": "判断下面内容是负能量还是正能量:"},
            #           {"role": "user", "content": "4. 中国科学家在量子计算领域取得重大突破，引领世界潮流"},
            #           {"role": "assistant", "content": "正能量"},
            #           {"role": "user", "content": "2. 某地党政干部因涉黑涉恶被查处，形象受损。"},
            #           {"role": "assistant", "content": "负能量"},
            #           {"role": "user", "content": "3. 中国成功研制多款新冠疫苗，全球抗疫贡献有目共睹"},
            #           {"role": "assistant", "content": "正能量"}],
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            # 使用examples参数来提供一些示例
            # examples=[
            #     ["1. 国内推出新的社会保险政策，让民生更加安定", "正能量"],
            #     ["3. 中国成功研制多款新冠疫苗，全球抗疫贡献有目共睹", "正能量"],
            #     ["5. 中国组建国家级大数据中心，促进数字经济发展", "正能量"],
            #     ["2. 某地党政干部因涉黑涉恶被查处，形象受损。", "负能量"],
            #     ["3. 某机构工作人员因职务犯罪被判刑，损害了国家形象。", "负能量"],
            #     ["10. 某地公共服务体系发展缓慢，民生问题突出。", "负能量"]
            # ]
            # stop=["\n"]
        )
        sentiment = response['choices'][0]['text']
        # sentiment = response['choices'][0]['message']['content']
        sentiments.append(sentiment)  # 将情感极性添加到列表中
    return sentiments


# 读取excel文件中的第一列前10条文本，并存储在一个列表中
df = pd.read_excel("D:\\doc\\信通院二期训练文本数据\\正能量测试.xlsx",
                   usecols=[0], header=None)
texts = df[0].tolist()
print('输入的文本', texts)

# 调用get_sentiments函数获取批量情感分析结果，并添加到df数据框中作为新的一列"Sentiment"
df["Sentiment"] = get_sentiments(texts)

# 将df数据框写入一个新的的excel文件中，覆盖原有内容
df.to_excel('D:\\doc\\信通院二期训练文本数据\\正能量测试检测结果.xlsx', index=False)

# 打印每条文本的检测结果
for i in range(len(texts)):
    print(f"Text: {texts[i]}\nSentiment: {df['Sentiment'][i]}\n")
