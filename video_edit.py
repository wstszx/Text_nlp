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
    response = model.generate_content(prompt, generation_config=generation_config)
    time.sleep(2)
    print(f"Response: {response.text}")
    return response.text


@RateLimiter(max_calls=5, period=60)
def match_content(script_analysis, media_analyses):
    """Matches spoken content with media material."""
    prompt = f"根据以下口播文案分析和媒体内容分析，为每个时间点匹配最合适的媒体素材：\n\n口播分析：{script_analysis}\n\n媒体分析：{media_analyses}"
    print(f"Prompt: {prompt}")
    response = model.generate_content(prompt, generation_config=generation_config)
    time.sleep(2)
    print(f"Response: {response.text}")
    return response.text


@RateLimiter(max_calls=5, period=60)
def generate_edit_plan(matches):
    """Generates a video editing plan."""
    prompt = f"根据以下内容匹配结果，生成一个详细的视频剪辑计划，包括每个片段的开始时间、持续时间和使用的素材：\n\n{matches}"
    print(f"Prompt: {prompt}")
    response = model.generate_content(prompt, generation_config=generation_config)
    time.sleep(2)
    print(f"Response: {response.text}")
    return response.text


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
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")


def load_media_clips(media_folder):
    """Loads all video and image files."""
    video_clips = {}
    image_clips = {}

    for media_file in os.listdir(media_folder):
        media_path = os.path.join(media_folder, media_file)
        if media_file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            video_clips[media_file] = VideoFileClip(media_path)
        elif media_file.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_clips[media_file] = ImageClip(media_path)

    print(f"Loaded {len(video_clips)} video clips and {len(image_clips)} image clips.")
    return video_clips, image_clips


def load_analysis_cache(cache_file):
    """从 JSON 文件加载分析缓存"""
    print(f"尝试从 {cache_file} 加载分析缓存")
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        print(f"已加载缓存数据：{cache_data}")
        return cache_data
    except json.JSONDecodeError:  # 捕获 JSONDecodeError
        print(f"缓存文件为空或无效。将使用空缓存开始。")
        return {}


def save_analysis_cache(cache_file, analysis_cache):
    """将分析缓存保存到 JSON 文件"""
    print(f"正在将分析缓存保存到 {cache_file}")
    print(f"分析缓存内容：{analysis_cache}")
    with open(cache_file, 'w') as f:
        json.dump(analysis_cache, f, indent=4)
    print(f"缓存已成功保存。")


def process_media(media_path, media_type, analysis_cache):
    """Process a single media file, using cache if available."""
    media_name = os.path.basename(media_path)
    if media_name in analysis_cache:
        print(f"Using cached analysis for {media_name}")
        return media_name, analysis_cache[media_name]

    analysis = analyze_media(media_path, media_type)
    if analysis:
        analysis_cache[media_name] = analysis
    return media_name, analysis


@RateLimiter(max_calls=5, period=60)
def check_media_sufficiency(script_analysis, media_analyses):
    """Checks if the available media material is sufficient for the script using Qwen-7B."""

    for script_part in script_analysis.splitlines():
        script_part = script_part.strip()
        if not script_part:
            continue
        match_found = False
        for media_name, media_analysis in media_analyses:
            prompt = f"口播文案 '{script_part}' 和媒体素材 '{media_name}' 的描述 '{media_analysis}' 是否表达一致？"
            print(f"Prompt: {prompt}")

            # 使用 Qwen/Qwen2-7B-Instruct
            sili_payload = {
                "model": "Qwen/Qwen2-7B-Instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4096
            }
            response = qwen_session.post(sili_url, json=sili_payload, headers=sili_headers)
            
            # 处理 Qwen API 响应
            if response.status_code == 200:
                answer = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"Response: {answer}")
                if "yes" in answer.lower() or "是" in answer.lower():
                    match_found = True
                    break
            else:
                print(f"Error calling Qwen API: {response.status_code}, {response.text}")
                return False  # API 调用出错，返回 False

        if not match_found:
            print(f"No matching media found for script part: {script_part}")
            return False  # 只要有一个 script_part 没有匹配，就返回 False

    return True  # 所有 script_part 都找到了匹配，返回 True


# Main workflow
def main():
    script_file_path = r"D:\doc\corrected_subtitle.srt"
    script = read_script_from_srt_file(script_file_path)

    script_analysis = analyze_script(script)
    print(f"Script analysis: {script_analysis}")

    media_folder = r"D:\videos\20240703"
    media_files = [os.path.join(media_folder, f) for f in os.listdir(media_folder)]

    cache_file = 'analysis_cache.json'
    analysis_cache = load_analysis_cache(cache_file)

    while True:
        # 使用线程池，限制并发数量
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_media = {
                executor.submit(process_media,
                                media_path,
                                'video' if media_path.endswith(('.mp4', '.avi', '.mov', '.mkv')) else 'image',
                                analysis_cache): media_path for media_path in media_files}

            media_analyses = []
            for future in concurrent.futures.as_completed(future_to_media):
                media_path = future_to_media[future]
                try:
                    media_name, analysis = future.result()
                    if analysis:
                        media_analyses.append((media_name, analysis))
                    print(f"Analysis for {media_name}: {analysis}")
                except Exception as exc:
                    print(f'{media_path} generated an exception: {exc}')

        # 保存更新后的分析缓存
        print(f"Analysis cache before saving: {analysis_cache}")
        save_analysis_cache(cache_file, analysis_cache)
        print(f"Analysis cache after saving: {analysis_cache}")

        # 检查媒体素材是否充足
        if check_media_sufficiency(script_analysis, media_analyses):
            print("Media material is sufficient. Proceeding with editing...")
            break
        else:
            print("Media material is insufficient. Please add more files and try again.")
            # 在此处可以添加暂停逻辑，等待用户添加更多文件
            input("Press Enter to continue...")
            # 重新加载媒体文件列表
            media_files = [os.path.join(media_folder, f) for f in os.listdir(media_folder)]

    # 素材充足，开始进行匹配和剪辑
    matches = match_content(script_analysis, media_analyses)
    print(f"Matches: {matches}")

    edit_plan = generate_edit_plan(matches)
    print(f"Edit plan: {edit_plan}")

    # Load all video and image material
    video_clips, image_clips = load_media_clips(media_folder)

    # Audio file path
    output_audio = r"D:\doc\output.wav"
    output_file = r"D:\doc\final_video.mp4"

    # Edit and generate the final video based on the editing plan
    edit_video(edit_plan, video_clips, image_clips, output_audio, output_file)

    print("Video editing plan:", edit_plan)


if __name__ == "__main__":
    main()