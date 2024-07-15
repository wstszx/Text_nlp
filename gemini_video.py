import os
import time
import google.generativeai as genai
from IPython.display import Markdown
import configparser

# 设置代理
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'


# 配置API密钥

config = configparser.ConfigParser()
config.read('video_edit_config.ini')
genai_api_key = config['API']['GENAI_API_KEY']
genai.configure(api_key=genai_api_key)

# 上传视频文件
video_file_name = r"C:\Users\Admin\Videos\1.mp4"
print("Uploading file...")
video_file = genai.upload_file(path=video_file_name)
print(f"Completed upload: {video_file.uri}")

# 检查文件是否准备就绪
while video_file.state.name == "PROCESSING":
    print('.', end='')
    time.sleep(10)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
    raise ValueError(video_file.state.name)

# 选择Gemini模型
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# 创建提示
prompt = "Summarize this video. Then create a quiz with answer key based on the information in the video."

# 发送LLM请求
print("Making LLM inference request...")
response = model.generate_content([video_file, prompt],
                                  request_options={"timeout": 600})

# 打印响应，渲染任何Markdown
print(response.text)

# 使用时间戳引用视频内容
# timestamp_prompt = "What happens at 00:30 in the video?"
# timestamp_response = model.generate_content([timestamp_prompt, video_file],
#                                             request_options={"timeout": 600})
# print(timestamp_response.text)

# # 转录视频并提供视觉描述
# transcribe_prompt = "Transcribe the audio, giving timestamps. Also provide visual descriptions."
# transcribe_response = model.generate_content([transcribe_prompt, video_file],
#                                              request_options={"timeout": 600})
# print(transcribe_response.text)

# 清理：删除上传的文件
genai.delete_file(video_file.name)
print(f'Deleted file {video_file.uri}')