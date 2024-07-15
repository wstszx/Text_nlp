import os
import google.generativeai as genai
from PIL import Image
from moviepy.editor import VideoFileClip
import tempfile

# 设置代理
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

# 配置API密钥
genai.configure(api_key="AIzaSyB93cUIGtfNVJOFQsC_dB-r8irJ6rRXWwY")

# 创建模型配置
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

print("配置信息:", generation_config)

# 创建模型实例
model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
)

# 图片分析函数
def analyze_image(image_path):
    img = Image.open(image_path)
    response = model.generate_content(["Analyze this image:", img])
    print("图片分析结果:", response.text)

# 视频分段分析函数
def analyze_video_segment(segment_path, segment_number):
    with open(segment_path, 'rb') as video_file:
        video_data = video_file.read()
    
    video_part = {
        "mime_type": "video/mp4",
        "data": video_data
    }

    response = model.generate_content([
        f"Analyze this video segment (Segment {segment_number}). Provide a summary of key events and subjects in this part of the video.",
        video_part
    ])
    return response.text

# 视频分析主函数
def analyze_video(video_path):
    print(f"准备分析视频文件...")
    
    with VideoFileClip(video_path) as video:
        duration = video.duration
        segment_duration = 60  # 每段60秒
        num_segments = int(duration / segment_duration) + 1

        for i in range(num_segments):
            start = i * segment_duration
            end = min((i + 1) * segment_duration, duration)
            
            segment = video.subclip(start, end)
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                segment_path = temp_file.name
                segment.write_videofile(segment_path, codec="libx264")
            
            print(f"分析视频段 {i+1}/{num_segments}...")
            result = analyze_video_segment(segment_path, i+1)
            print(f"段 {i+1} 分析结果: {result}")
            
            os.unlink(segment_path)  # 删除临时文件

    print("视频分析完成")

try:
    # 使用示例
    image_path = "screenshot.png"
    video_path = r"C:\Users\Admin\Videos\工控22 2024-05-26 212016.mp4"

    print("开始分析图片...")
    analyze_image(image_path)

    print("开始分析视频...")
    analyze_video(video_path)

except Exception as e:
    print("发生错误:", e)