import subprocess
import cv2
import numpy as np
import paddleocr

# 创建paddleocr对象，使用中英文模型
ocr = paddleocr.PaddleOCR(lang="ch")

# 通过ADB获取截图并将其保存到本地
subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])
subprocess.run(["adb", "pull", "/sdcard/screen.png", "."])

# 读取截图
img = cv2.imread("screen.png")

# 使用paddleocr进行文字检测和识别，返回结果列表
results = ocr.ocr(img)
# 遍历结果列表，打印每个文本框的坐标、内容和准确率
result_lines = [line for result in results for line in result]
for box, (text, score) in result_lines:
    print(f"box: {box}")
    print(f"text: {text}")
    print(f"score: {score}")
