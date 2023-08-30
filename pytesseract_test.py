import pytesseract
import numpy as np
import cv2
import time
from PIL import ImageGrab

# 指定截图范围
bbox = (0, 0, 500, 500)

# 不断循环截图并识别文本
while True:
    # 获取屏幕截图
    img = ImageGrab.grab(bbox=bbox)
    
    # 将PIL图像转换为OpenCV格式
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # 使用Pytesseract进行OCR识别
    text = pytesseract.image_to_string(img)
    
    # 打印识别结果
    print(text)
    
    # 暂停1秒后继续循环
    time.sleep(1)