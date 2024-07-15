import os
import time
import threading
import concurrent.futures
import json
import configparser
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from pysrt import SubRipFile
import google.generativeai as genai

# 设置代理
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

# 全局超时时间设置 (单位：秒)
REQUEST_TIMEOUT = 1200

# 从 config.ini 文件中读取 API 密钥
config = configparser.ConfigParser()
config.read('video_edit_config.ini')
genai_api_key = config['API']['GENAI_API_KEY']

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

CACHE_FILE = 'media_analysis_cache.json'


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
                    print(f"Rate limit reached. Sleeping for{sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                self.calls.append(time.time())
            return f(*args, **kwargs)
        return wrapped


def load_cache():
    """Loads analysis results cache from a JSON file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Saves analysis results cache to a JSON file。"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)


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
    """Analyzes the content of a video or image using Google Gemini API。"""
    prompt = f"描述这个{media_type}的内容："
    print(f"Uploading {media_type}: {media_path}")
    media_file = genai.upload_file(path=media_path)
    print(f"Completed upload: {media_file.uri}")

    # 检查文件状态
    while media_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(10)
        media_file = genai.get_file(media_file.name)

    if media_file.state.name != "ACTIVE":
        raise ValueError(f"File processing failed: {media_file.state.name}")

    print(f"Prompt: {prompt}")
    print("Generating content analysis...")
    response = model.generate_content([prompt, media_file], generation_config=generation_config, stream=True)

    analysis = ""
    for chunk in response:
        analysis += chunk.text
        print(f"Received chunk: {chunk.text}")

    return analysis


@RateLimiter(max_calls=5, period=60)
def analyze_script(script):
    """Analyzes the spoken script and extracts key content and timestamps。"""
    prompt = f"分析以下口播文案，提取关键内容和对应的时间点：\n\n{script}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            start_time = time.time()
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}. Retrying after {delay} seconds...")
            time.sleep(delay)
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")


@RateLimiter(max_calls=5, period=60)
def match_content(script_analysis, media_analyses):
    """Matches spoken content with media material。"""
    prompt = f"根据以下口播文案分析和媒体内容分析，为每个时间点匹配最合适的媒体素材：\n\n口播分析：{script_analysis}\n\n媒体分析：{media_analyses}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}. Retrying after {delay} seconds...")
            time.sleep(delay)
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")


@RateLimiter(max_calls=5, period=60)
def generate_edit_plan(matches):
    """Generates a video editing plan。"""
    prompt = f"根据以下内容匹配结果，生成一个详细的视频剪辑计划，包括每个片段的开始时间、持续时间和使用的素材：\n\n{matches}"
    print(f"Prompt: {prompt}")
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            attempts += 1
            delay *= 2
            print(f"Attempt {attempts} failed: {e}.Retrying after {delay} seconds...")
            time.sleep(delay)
    raise Exception("Max attempts reached. Could not connect to the Google Gemini API.")


def read_script_from_srt_file(file_path):
    """Reads spoken script from an SRT subtitle file."""
    subs = SubRipFile.open(file_path)
    script = "\n".join([f"{sub.start} --> {sub.end}\n{sub.text}" for sub in subs])
    return script


def parse_edit_plan(edit_plan):
    """Parses the edit plan and returns segment information."""
    segments = []
    in_segments_section = False

    for line in edit_plan.splitlines():
        line = line.strip()
        print(f"Parsing line: {line}")

        # 标记段落开始
        if line.startswith("**片段") or line.startswith("**Segment"):
            in_segments_section = True
            continue

        # 跳过空行和无关行
        if not line or not in_segments_section:
            continue

        # 解析段落内容
        parts = line.split('|')
        if len(parts) >= 5:
            try:
                start_time = time_to_seconds(parts[1].strip())
                duration = time_to_seconds(parts[2].strip())
                description = parts[3].strip()
                media_name = parts[4].strip().split('：')[-1].strip()

                media_type = "video" if ".mp4" in media_name.lower() else "image"
                segments.append({
                    'start_time': start_time,
                    'duration': duration,
                    'media_type': media_type,
                    'media_name': media_name
                })
                print(f"Successfully parsed segment: {segments[-1]}")
            except ValueError as e:
                print(f"Skipping line due to parsing error: {line}, Error: {e}")
        else:
            print(f"Skipping line with incorrect format: {line}")

    if not segments:
        print(f"No valid segments found in edit plan.")
    return segments


def time_to_seconds(time_str):
    """Converts time in the format HH:MM:SS to seconds."""
    h, m, s = [float(unit) for unit in time_str.split(':')]
    return h * 3600 + m * 60 + s


def edit_video(edit_plan, video_clips, image_clips, output_audio, output_file):
    """Edits the video according to the editing plan."""
    segments = parse_edit_plan(edit_plan)
    print("Segments:", segments)
    if not segments:
        raise ValueError("No valid segments were found. The video editing process cannot proceed.")

    clips = []

    for segment in segments:
        print(f"Processing segment: {segment}")
        if segment['media_type'] == 'video':
            clip = video_clips.get(segment['media_name'], None)
            if clip:
                clips.append(clip.subclip(0, segment['duration']))
            else:
                print(f"Warning: Video file {segment['media_name']} not found.")
        else:  # Assuming 'image'
            clip = image_clips.get(segment['media_name'], None)
            if clip:
                clips.append(clip.set_duration(segment['duration']))
            else:
                print(f"Warning: Image file {segment['media_name']} not found.")

        print(f"Added clip: {clip if clip else 'None'}")

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
        # 加载缓存
        cache = load_cache()

        script = read_script_from_srt_file(script_file)
        print("Script:", script)
        script_analysis = analyze_script(script)
        print("Script analysis:", script_analysis)

        media_analyses = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_media = {
                executor.submit(analyze_media_with_cache, file, "video" if file.endswith(".mp4") else "image", cache): file
                for file in media_files
            }
            for future in concurrent.futures.as_completed(future_to_media):
                media_file = future_to_media[future]
                try:
                    media_analyses[media_file] = future.result()
                except Exception as exc:
                    print(f"{media_file} generated an exception: {exc}")

        print("Media analyses:", media_analyses)

        # 保存缓存
        save_cache(cache)

        matches =match_content(script_analysis, media_analyses)
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


def analyze_media_with_cache(media_path, media_type, cache):
    """Analyzes the content of a video or image with caching support。"""
    media_name = os.path.basename(media_path)
    if media_name in cache:
        print(f"Using cached analysis for {media_name}.")
        return cache[media_name]

    analysis = analyze_media(media_path, media_type)
    cache[media_name] = analysis
    return analysis


if __name__ == "__main__":
    script_file = r"D:\doc\corrected_subtitle.srt"
    media_files = [r"D:\videos\20240703\2.mp4", r"D:\videos\20240703\3.mp4"]
    output_audio = r"D:\doc\output.wav"
    output_file = r"D:\doc\final_video.mp4"
    main(script_file, media_files, output_audio, output_file)