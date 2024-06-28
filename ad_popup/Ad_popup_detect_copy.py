import os
import time
import logging
import uiautomator2 as u2
import subprocess
import cv2
import paddleocr
import json
import base64
import requests
import configparser
import codecs
import threading
import keyboard
from concurrent.futures import ThreadPoolExecutor


# 创建paddleocr对象，使用中英文模型
ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang="ch")

# 图像分类API参数
PARAMS = {
    "threshold": 0.5,
    "classify_dimension": "simple",
    "type": "object_detection"
}


def connect_device(serial: str) -> u2.Device:
    try:
        return u2.connect(serial)
    except u2.exceptions.ConnectDeviceTimeoutError as e:
        logging.error(f"连接设备失败: {e}")
        return None


def read_popup_texts(file_path: str) -> list:
    popup_texts = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                text, priority = line.strip().split()
                popup_texts.append((str(text), int(priority)))
    except FileNotFoundError as e:
        logging.error(f"文件不存在: {e}")
    except ValueError as e:
        logging.error(f"文件格式错误: {e}")
    return popup_texts


def restart_app(device: u2.Device, package_name: str, apk_path: str) -> None:
    device.app_stop(package_name)
    # device.app_clear(package_name)
    device.app_start(package_name)


def wait_for_app_load(device: u2.Device, home_tab_resource_id: str, timeout: int) -> None:
    device(resourceId=home_tab_resource_id).wait(timeout=timeout)


def match_text(device: u2.Device, ocr_results: list, target_texts: str, model_api_url: str, api_key: str, secret_key: str) -> bool:
    result_lines = [(box, text) 
                    for result in ocr_results 
                    for box, (text, score) in result]

    # print("ocr_results", ocr_results)
    # print("result_lines", result_lines)
    # print("target_text", target_texts)
    for box, text in result_lines:
        if text in target_texts:
            x1, y1 = box[0][0], box[0][1]
            x2, y2 = box[2][0], box[2][1]
            click_coordinates = (x2-x1)/2 + x1, (y2-y1)/2 + y1
            print(f"ocr匹配到了关闭按钮文字: {text}, 点击坐标: {click_coordinates}")
            x, y = click_coordinates
            device.click(x, y)
            return True

    # 如果ocr未匹配到，则调用图像分类API识别关闭按钮图标
    with open("./screen.png", 'rb') as f:
        base64_data = base64.b64encode(f.read())
        base64_str = base64_data.decode('UTF8')
    PARAMS["image"] = base64_str

    auth_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    auth_resp = requests.get(auth_url)
    auth_resp_json = auth_resp.json()
    access_token = auth_resp_json["access_token"]
    request_url = f"{model_api_url}?access_token={access_token}"
    response = requests.post(url=request_url, json=PARAMS)
    response_json = response.json()
    response_str = json.dumps(response_json, indent=4, ensure_ascii=False)
    logging.info(f"图像分类API返回结果: {response_str}")
    # 解析API返回结果，点击关闭按钮
    for item in response_json["results"]:
        if "关闭" in item["name"]:
            x1, y1, x2, y2 = item["location"]["left"], item["location"]["top"], item["location"]["left"] + \
                item["location"]["width"], item["location"]["top"] + \
                item["location"]["height"]
            click_coordinates = (x2-x1)/2 + x1, (y2-y1)/2 + y1

            print(f"图像识别api找到关闭按钮, 点击坐标: {click_coordinates}")
            x, y = click_coordinates
            device.click(x, y)
            return True
    return False


def main(config_path: str = "config.ini") -> None:
    config = configparser.ConfigParser()
    with codecs.open(config_path, 'r', encoding='utf-8') as f:
        config.read_file(f)

    serial = u2.connect().serial
    package_name = config.get("app", "package_name")
    home_tab_resource_id = config.get("app", "home_tab_resource_id")
    apk_path = config.get("paths", "apk_path")
    text_file_path = config.get("paths", "text_file_path")
    timeout = config.getint("app", "timeout")
    model_api_url = config.get("easydl", "model_api_url")
    api_key = config.get("easydl", "api_key")
    secret_key = config.get("easydl", "secret_key")

    popup_texts = read_popup_texts(text_file_path)
    # print("popup_texts", popup_texts)
    target_texts = set(popup_text for popup_text, _ in popup_texts)
    # print("target_texts", target_texts)
    device = connect_device(serial)
    if device is None:
        return

    restart_app(device, package_name, apk_path)
    # wait_for_app_load(device, home_tab_resource_id, timeout)

    # for i, (popup_text, priority) in enumerate(popup_texts):
    #     device.xpath.when(popup_text).click()
    #     device.xpath.watch_background(1)

    # 在单独的线程中启动target函数
    ocr_thread = threading.Thread(target=ocr_loop(
        device, target_texts, model_api_url, api_key, secret_key))
    ocr_thread.start()


def ocr_loop(device, target_texts, model_api_url, api_key, secret_key):

    while True:
        subprocess.run(["adb", "shell", "screencap",
                       "-p", "/sdcard/screen.png"])
        subprocess.run(["adb", "pull", "/sdcard/screen.png", "."])
        img = cv2.imread("./screen.png")
        ocr_results = ocr.ocr(img)
        
        match_text(device, ocr_results, target_texts, model_api_url, api_key, secret_key)
           
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    keyboard.add_hotkey('ctrl+c', lambda: exit(0))
