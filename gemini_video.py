import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 设置 Clash 代理
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7899'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7899'

# 从环境变量中获取API密钥
api_key = os.getenv('GENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the 'GENAI_API_KEY' environment variable.")

# 设置API密钥
genai.configure(api_key=api_key)

# 初始化模型
model = genai.GenerativeModel('gemini-1.5-pro')

# 设置生成参数
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    },
]

# 视频文件路径
video_path = r"D:\videos\2103099-uhd_3840_2160_30fps.mp4"

def wait_for_file_processing(file):
    while file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(10)
        file = genai.get_file(file.name)
    
    if file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {file.state.name}")
    
    return file

def upload_and_analyze(retries=3):
    for attempt in range(retries):
        try:
            # 上传视频文件
            print("Uploading file...")
            video_file = genai.upload_file(path=video_path)
            print(f"Completed upload: {video_file.uri}")

            # 等待文件处理完成
            print("Waiting for file processing to complete...")
            video_file = wait_for_file_processing(video_file)
            print("File is now ready for use.")

            if video_file.state.name == "ACTIVE":
                # 创建提示
                prompt = "分析这个视频并描述其主要内容、场景和事件。"

                # 生成响应
                print("Generating content...")
                response = model.generate_content(
                    [prompt, video_file],
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    stream=True
                )

                # 打印响应
                for chunk in response:
                    print(chunk.text)
                
                return  # 如果成功，退出函数
            else:
                print(f"File is not in ACTIVE state. Current state: {video_file.state.name}")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("All attempts failed.")

if __name__ == "__main__":
    upload_and_analyze()
