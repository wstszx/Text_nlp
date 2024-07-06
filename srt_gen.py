import whisper
import os

def format_timestamp(seconds):
    """
    将时间戳格式化为 SRT 文件的时间格式

    Args:
        seconds: 时间戳（以秒为单位）

    Returns:
        格式化后的时间戳字符串
    """
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def generate_subtitles(file_path, ffmpeg_path):
    """
    使用 OpenAI Whisper 模型生成音频或视频文件的字幕文件.

    Args:
        file_path: 音频或视频文件的路径.
        ffmpeg_path: ffmpeg 可执行文件的路径.
    """

    # 检查提供的 ffmpeg_path 是否正确
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"找不到指定的 ffmpeg 可执行文件: {ffmpeg_path}")

    # 设置 ffmpeg 环境变量
    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]

    # 初始化 Whisper 模型
    model = whisper.load_model("tiny")  # 使用大型模型提高准确性

    # 加载音频文件并进行语音识别
    result = model.transcribe(file_path, language='zh') # 指定语言为中文

    # 生成 SRT 文件内容
    srt_content = ""
    for i, segment in enumerate(result["segments"]):
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        text = segment["text"].strip()
        srt_content += f"{i + 1}\n{start_time} --> {end_time}\n{text}\n\n"

    # 打印识别结果
    print("字幕:")
    print(srt_content)

    # 将字幕保存到 SRT 文件
    with open(file_path + ".srt", "w", encoding="utf-8") as f:
        f.write(srt_content)


if __name__ == "__main__":
    # 直接在此处指定音频或视频文件的路径和 ffmpeg 可执行文件的路径
    file_path = r"D:\download\ffmpeg-2024-05-15-git-7b47099bc0-full_build\ffmpeg-2024-05-15-git-7b47099bc0-full_build\bin\output.wav"
    ffmpeg_path = r"D:\download\ffmpeg-2024-05-15-git-7b47099bc0-full_build\ffmpeg-2024-05-15-git-7b47099bc0-full_build\bin\ffmpeg.exe"
    
    generate_subtitles(file_path, ffmpeg_path)