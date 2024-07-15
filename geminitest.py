import os
import configparser
import google.generativeai as genai

# 设置代理
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

# 读取配置文件
config = configparser.ConfigParser()
config.read('video_edit_config.ini')
genai_api_key = config['API']['GENAI_API_KEY']

# 配置 Generative AI
genai.configure(api_key=genai_api_key)

# 创建模型配置
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

print("配置信息:", generation_config)

try:
    # 创建 Gemini 模型实例
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config
    )

    # 开始视频分析会话
    video_analysis_session = model.start_chat(history=[])
    print("视频分析会话开始")

    # 发送视频分析请求
    video_file_path = r"D:\videos\20240703\3.mp4"
    response = video_analysis_session.send_message(f"分析这里面的内容: {video_file_path}")

    # 打印视频分析结果
    print("视频分析结果:", response.text)

except Exception as e:
    print("发生错误:", e)