import subprocess
import time
import cv2

# YouTube 直播链接
youtube_url = "https://www.youtube.com/watch?v=uSkT4MwpCYA"

# 代理设置 (如果需要)
proxy = "http://127.0.0.1:7899"  # 将此值替换为你的代理地址和端口

# 固定图片名称
output_filename = "live_frame.jpg"

# 获取直播流的 m3u8 地址
def get_m3u8_url():
    try:
        command = ["yt-dlp", "--get-url", "--proxy", proxy, youtube_url]
        process = subprocess.run(command, capture_output=True, text=True)
        m3u8_url = process.stdout.strip()
        return m3u8_url
    except Exception as e:
        print(f"获取 m3u8 地址失败: {e}")
        return None

# 获取一帧直播视频图像并保存为固定名称
def get_frame():
    m3u8_url = get_m3u8_url()
    if m3u8_url:
        try:
            command = [
                "D:\\download\\ffmpeg-2024-01-20-git-6c4388b468-full_build\\ffmpeg-2024-01-20-git-6c4388b468-full_build\\bin\\ffmpeg",
                "-http_proxy", proxy,  # 添加代理设置
                "-i",
                m3u8_url,
                "-vframes",
                "1",
                "-f",
                "image2",
                "-y",  # 添加 -y 选项，强制覆盖
                output_filename,
            ]
            subprocess.run(command)
            print(f"已保存图像: {output_filename}")
            return output_filename
        except Exception as e:
            print(f"获取直播帧失败: {e}")
            return None

# 使用 OpenCV 识别二维码
def decode_qrcode(image_path):
    try:
        image = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(image)
        if bbox is not None:
            print(f"二维码内容: {data}")
    except Exception as e:
        print(f"二维码识别失败: {e}")

# 每隔 60 秒获取一帧图像并识别二维码
while True:
    image_path = get_frame()
    if image_path:
        decode_qrcode(image_path)
    time.sleep(60)