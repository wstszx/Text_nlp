import os
import time
import threading
import concurrent.futures
import google.generativeai as genai
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
import cv2
from pysrt import SubRipFile
import configparser
import json
import requests
from google.api_core.exceptions import ServiceUnavailable

# 全局超时时间设置 (单位：秒)
REQUEST_TIMEOUT = 10 

# 从 config.ini 文件中读取 API 密钥
config = configparser.ConfigParser()
config.read('video_edit_config.ini')
genai_api_key = config['API']['GENAI_API_KEY']
sili_api_key = config['API']['SILI_API_KEY']

if not genai_api_key:
    raise ValueError("API key not found. Please set the 'GENAI_API_KEY' in config.ini file.")

# 设置 Google Gemini API 密钥
genai.configure(api_key=genai_api_key)

# 初始化 Google Gemini 模型
model = genai.GenerativeModel('gemini-1.5-pro')

# 设置 Google Gemini 生成参数
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# 创建一个信号量，限制并发请求数量
semaphore = threading.Semaphore(2)

# 硅基智能 API 相关设置
sili_url = "https://api.siliconflow.cn/v1/chat/completions"
sili_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {sili_api_key}"
}

# 创建两个 Session 对象，分别用于调用 Gemini 和 Qwen API
gemini_session = requests.Session()
qwen_session = requests.Session()

# 设置 Clash 代理 (只针对 gemini_session)
gemini_session.proxies = {
    'http': 'http://127.0.0.1:7899',
    'https': 'http://127.0.0.1:7899',
}

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            with self.lock:
                now = time.time()
                self.calls = [c for c in self.calls if now - c < self.period]
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.period - (now - self.calls[0])
                    print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                self.calls.append(time.time())
            return f(*args, **kwargs)
        return wrapped

@RateLimiter(max_calls=5, period=60)
def wait_for_file_processing(file):
    while file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(10)
        file = genai.get_file(file.name)
    print(f"File processing state: {file.state.name}")
    if file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {file.state.name}")
    return file

@RateLimiter(max_calls=5, period=60)
def analyze_media(media_path, media_type):
    """Analyzes the content of a video or image."""
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            with semaphore:
                print(f"Uploading {media_type}: {media_path}")
                media_file = genai.upload_file(path=media_path)
                print(f"Completed upload: {media_file.uri}")
                print("Waiting for file processing to complete...")
                media_file = wait_for_file_processing(media_file)
                print("File is now ready for use.")
                if media_file.state.name == "ACTIVE":
                    prompt = f"描述这个{media_type}的内容："
                    print(f"Prompt: {prompt}")
                    print("Generating content analysis...")
                    start_time = time.time()
                    response = model.generate_content(
                        [prompt, media_file],
                        generation_config=generation_config,
                        stream=True
                    )
                    analysis = ""
                    for chunk in response:
                        analysis += chunk.text
                        print(f"Received chunk: {chunk.text}")
                        time.sleep(2)
                    return analysis
                else:
                    print(f"File is not in ACTIVE state. Current state: {media_file.state.name}")
                    return None
        except Exception as e:
            attempts += 1
            delay *= 2
            print(f"Analysis attempt {attempts} failed for {media_path}: {e}")
            print(f"Retrying after {delay} seconds...")
            time.sleep(delay)
    print(f"Analysis failed for {media_path} after {max_attempts} attempts.")
    return None

@RateLimiter(max_calls=5, period=60)
def analyze_script(script):
    """Analyzes the spoken script and extracts key content and timestamps."""
    prompt = f"分析以下口播文案，提取关键内容和对应的时间点：\n\n{script}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            start_time = time.time()
            response = model.generate_content(prompt, generation_config=generation_config)
            while time.time() - start_time < REQUEST_TIMEOUT:  # Timeout set to 1200 seconds
                time.sleep(2)
            print(f"Response: {response.text}")
            return response.text
        except ServiceUnavailable as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}. Retrying after {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise e
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")

@RateLimiter(max_calls=5, period=60)
def match_content(script_analysis, media_analyses):
    """Matches spoken content with media material."""
    prompt = f"根据以下口播文案分析和媒体内容分析，为每个时间点匹配最合适的媒体素材：\n\n口播分析：{script_analysis}\n\n媒体分析：{media_analyses}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            start_time = time.time()
            response = model.generate_content(prompt, generation_config=generation_config)
            while time.time() - start_time < REQUEST_TIMEOUT:  # Timeout set to 1200 seconds
                time.sleep(2)
            print(f"Response: {response.text}")
            return response.text
        except ServiceUnavailable as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}. Retrying after {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise e
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")

@RateLimiter(max_calls=5, period=60)
def generate_edit_plan(matches):
    """Generates a video editing plan."""
    prompt = f"根据以下内容匹配结果，生成一个详细的视频剪辑计划，包括每个片段的开始时间、持续时间和使用的素材：\n\n{matches}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            start_time = time.time()
            response = model.generate_content(prompt, generation_config=generation_config)
            while time.time() - start_time < REQUEST_TIMEOUT:  # Timeout set to 1200 seconds
                time.sleep(2)
            print(f"Response: {response.text}")
            return response.text
        except ServiceUnavailable as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}. Retrying after {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise e
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")

def read_script_from_srt_file(file_path):
    """Reads spoken script from an SRT subtitle file."""
    subs = SubRipFile.open(file_path)
    script = "\n".join([f"{sub.start} --> {sub.end}\n{sub.text}" for sub in subs])
    return script

def parse_edit_plan(edit_plan):
    """Parses the edit plan and returns segment information."""
    segments = []
    for line in edit_plan.splitlines():
        print(f"Parsing line: {line}")
        parts = line.split(',')
        if len(parts) == 4:
            start_time, duration, media_type, media_name = parts
            segments.append({
                'start_time': float(start_time.strip()),
                'duration': float(duration.strip()),
                'media_type': media_type.strip(),
                'media_name': media_name.strip()
            })
            print(f"Successfully parsed segment: {segments[-1]}")
        else:
            print(f"Skipping line with incorrect format: {line}")
    return segments

def edit_video(edit_plan, video_clips, image_clips, output_audio, output_file):
    """Edits the video according to the editing plan."""
    segments = parse_edit_plan(edit_plan)
    print("Segments:", segments)
    clips = []

    for segment in segments:
        print(f"Processing segment: {segment}")
        if segment['media_type'] == 'video':
            clip = video_clips[segment['media_name']].subclip(0, segment['duration'])
        else:
            clip = image_clips[segment['media_name']].set_duration(segment['duration'])
        clips.append(clip)
        print(f"Added clip: {clip}")
    print("Clips:", clips)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Add audio
    print("Adding audio...")
    audio_clip = AudioFileClip(output_audio)
    final_clip = final_clip.set_audio(audio_clip)

    # Output the final video
    print(f"Writing final video to {output_file}...")
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
    print(f"Final video written to {output_file}.")

def main(script_file, media_files, output_audio, output_file):
    try:
        script = read_script_from_srt_file(script_file)
        print("Script:", script)
        script_analysis = analyze_script(script)
        print("Script analysis:", script_analysis)

        media_analyses = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_media = {executor.submit(analyze_media, file, "video" if file.endswith(".mp4") else "image"): file for file in media_files}
            for future in concurrent.futures.as_completed(future_to_media):
                media_file = future_to_media[future]
                try:
                    media_analyses[media_file] = future.result()
                except Exception as exc:
                    print(f"{media_file} generated an exception: {exc}")

        print("Media analyses:", media_analyses)
        matches = match_content(script_analysis, media_analyses)
        print("Matches:", matches)

        edit_plan = generate_edit_plan(matches)
        print("Edit plan:", edit_plan)

        # Prepare video and image clips
        video_clips = {file: VideoFileClip(file) for file in media_files if file.endswith(".mp4")}
        image_clips = {file: ImageClip(file) for file in media_files if file.endswith((".png", ".jpg", ".jpeg"))}

        # Edit video according to the edit plan
        edit_video(edit_plan, video_clips, image_clips, output_audio, output_file)
        print("Video editing completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    script_file = r"D:\doc\corrected_subtitle.srt"
    media_files = [r"D:\videos\20240703\2.mp4", r"D:\videos\20240703\3.mp4"]
    output_audio = r"D:\doc\output.wav"
    output_file = r"D:\doc\final_video.mp4"
    main(script_file, media_files, output_audio, output_file)
