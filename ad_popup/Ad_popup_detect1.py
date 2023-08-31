import os
import time
import logging
import uiautomator2 as u2


def connect_device(serial):
    try:
        return u2.connect_usb(serial=serial)
    except u2.exceptions.ConnectDeviceTimeoutError as e:
        logging.error(f"连接设备失败: {e}")
        return None


def read_popup_texts(file_path):
    popup_texts = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                text, priority = line.split()
                popup_texts.append((str(text), int(priority)))
    except FileNotFoundError as e:
        logging.error(f"文件不存在: {e}")
    except ValueError as e:
        logging.error(f"文件格式错误: {e}")
    return popup_texts


def restart_app(device, package_name):
    device.app_stop(package_name)
    device.app_start(package_name)


def wait_for_app_load(device, home_tab_resource_id, timeout=60):
    device(resourceId=home_tab_resource_id).wait(timeout=timeout)


def main():
    try:
        apk_path = "D:\\download\\拼多多官方.apk"
        text_file_path = "D:\\doc\\其它\\Pop_ups_close_text.txt"
        serial = u2.connect().serial
        package_name = 'com.xunmeng.pinduoduo'
        home_tab_resource_id = "com.xunmeng.pinduoduo:id/pdd"

        device = connect_device(serial)
        if device is None:
            return

        wait_for_app_load(device, home_tab_resource_id)
        restart_app(device, package_name)
        popup_texts = read_popup_texts(text_file_path)

        # 使用watcher属性监控特定文本
        for text, priority in popup_texts:
            logging.info(f"监控文本: {text}")
            device.xpath.when(text).click()
            device.xpath.watch_background(1)

        while True:
            time.sleep(1)
    finally:
        device.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()