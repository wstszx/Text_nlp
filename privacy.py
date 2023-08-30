import openai  # 导入openai库
import json  # 导入json库

openai.api_key = "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"  # 设置你的API密钥
engine = "davinci"  # 选择一个模型，比如davinci
# 你想要输入的文本
prompt = '判断下面内容是否有不合理的算法机制机理。\n\n包含两个字段：\n\n- exist: 一个布尔值，表示是否存在不合理的算法机制机理。\n- reasons: 一个字符串数组，表示不合理的算法机制机理的原因。\n\n隐私协议：\n\n我们收集并处理您使用我们的服务时提供或产生的信息，包括：\n\n- 账户信息：当您注册或登录我们的服务时，我们会收集您提供的手机号码、邮箱地址、密码等信息。\n- 用户内容：当您使用我们的服务时，我们会收集您上传或发布的文字、图片、视频、音频等内容。\n- 通讯录信息：当您使用我们的服务时，我们会请求您授权访问您的通讯录，以便为您提供好友推荐、添加好友等功能。\n- 设备信息：当您使用我们的服务时，我们会自动收集您的设备型号、操作系统版本、唯一设备标识符、IP地址等信息。\n- 位置信息：当您使用我们的服务时，我们会根据您的设备设置和授权，收集您的地理位置信息，以便为您提供基于位置的服务，如附近的人、附近的店铺等。\n- 行为信息：当您使用我们的服务时，我们会记录您的服务使用情况，如访问时间、停留时间、点击次数等。\n- 日志信息：当您使用我们的服务时，我们会自动记录您的浏览器类型、语言设置、访问日期和时间等信息。\n\n输出结果：\n\n{\n'

response = openai.Completion.create(  # 调用Completion API
    engine=engine,  # 指定模型
    prompt=prompt,  # 指定输入
    max_tokens=200,  # 设置最大输出长度为200个token
    stop="\n}",  # 设置停止符为换行符和大括号
    temperature=0.5,  # 设置温度为0.5
    top_p=0.9,  # 设置top_p为0.9
    logprobs=10,  # 设置返回前10个最可能token及其概率
    presence_penalty=0.1,  # 设置重复词语惩罚系数为0.1
    frequency_penalty=0.1  # 设置稀有词语惩罚系数为0.1
)
# 获取输出结果并去除首尾空格，并添加换行符和大括号
result = response["choices"][0]["text"].strip()
print(result)  # 打印输出结果

# data = json.loads(result)  # 将输出结果转换为json对象
# if data["exist"]:  # 如果存在不合理算法机制机理
#     print("该app存在不合理算法机制机理")
#     print("原因如下：")
#     for reason in data["reasons"]:  # 遍历原因数组
#         print("- " + reason)  # 打印每个原因
# else:  # 否则不存在不合理算法机制机理
#     print("该app不存在不合理算法机制机理")
