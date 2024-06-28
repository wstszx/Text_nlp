import os

import google.generativeai as genai

# 设置代理
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

genai.configure(api_key="")

# 创建模型配置
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  # 注意：移除了不存在的属性 'response_mime_type'
}

print("配置信息:", generation_config)

try:
    # 根据最新API文档创建模型实例，确保已删除不支持的参数
    model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      generation_config=generation_config,
      # 根据需要调整安全设置
    )

    chat_session = model.start_chat(history=[])
    print("会话开始")

    response = chat_session.send_message("世界最大的牛")
    print("问题:", chat_session)

    print("响应文本:", response.text)
except Exception as e:
    # 打印出异常信息
    print("发生错误:", e)
