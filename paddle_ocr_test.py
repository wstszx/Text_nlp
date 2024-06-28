import subprocess
import cv2
import numpy as np
import paddleocr
import time
import re

# 创建paddleocr对象，使用中英文模型
ocr = paddleocr.PaddleOCR(lang="ch")

device_serial_number = "AVYYUT1708002110"

def find_closest_number(target_text, results):
    """
    找到离目标文本纵坐标最近，且横坐标有重合的两位小数数字

    Args:
        target_text (str): 目标文本
        results (list): OCR结果列表

    Returns:
        str: 最近的两位小数数字，如果找不到则返回None
    """
    target_y = None
    target_x_range = None
    closest_number = None
    min_distance = float('inf')

    # print(f"查找目标文本: {target_text}")
    for box, (text, score) in results:
        # print(f"  - 文本: {text}, 坐标: {box}, 得分: {score}")
        if target_text in text:
            target_y = box[0][1]
            target_x_range = (box[0][0], box[1][0])  # 获取目标文本的横坐标范围
            # print(f"    找到目标文本，纵坐标: {target_y}, 横坐标范围: {target_x_range}")
            break

    if target_y is not None:
        for box, (text, score) in results:
            # 使用正则表达式匹配两位小数的数字
            match = re.search(r"\d+\.\d+", text)
            if match:
                # 检查数字的横坐标范围是否与目标文本有重合
                number_x_range = (box[0][0], box[1][0])
                if max(target_x_range[0], number_x_range[0]) < min(target_x_range[1], number_x_range[1]):
                    distance = abs(box[0][1] - target_y)
                    # print(f"  - 文本: {text}, 距离: {distance}, 纵坐标: {box[0][1]}, 横坐标范围: {number_x_range}")
                    if distance < min_distance:
                        min_distance = distance
                        closest_number = match.group(0)
                        # print(f"    更新最近数字: {closest_number}")

    return closest_number

while True:
    # 通过ADB获取截图并将其保存到本地
    subprocess.run(["adb", "-s", device_serial_number, "shell", "screencap", "-p", "/sdcard/screen.png"])
    subprocess.run(["adb", "-s", device_serial_number, "pull", "/sdcard/screen.png", "."])

    # 读取截图
    img = cv2.imread("screen.png")

    # 使用paddleocr进行文字检测和识别，返回结果列表
    results = ocr.ocr(img)
    result_lines = [line for result in results for line in result]

    # 打印所有识别到的文本和坐标
    # print("识别到的文本:")
    # for box, (text, score) in result_lines:
    #     print(f"  - 文本: {text}, 坐标: {box}, 得分: {score}")

    # 检查是否匹配到“测试意见”和“网络诊断”
    found_test_opinion = False
    found_network_diagnosis = False
    for _, (text, _) in result_lines:
        if text == "测试意见":
            found_test_opinion = True
        if text == "网络诊断":
            found_network_diagnosis = True

    # 如果匹配到，则获取相关信息
    if found_test_opinion and found_network_diagnosis:
        download_speed = find_closest_number("下载速度", result_lines)
        upload_speed = find_closest_number("上传速度", result_lines)

        print(f"下载速度: {download_speed}")
        print(f"上传速度: {upload_speed}")

    # 暂停一段时间
    time.sleep(1)