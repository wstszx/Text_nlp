import cv2
import numpy as np

def compare_images(image_path1, image_path2):
    # 读取两张图片
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    # 将两张图片调整至相同的尺寸
    height1, width1 = img1.shape[:2]
    height2, width2 = img2.shape[:2]
    new_height, new_width = min(height1, height2), min(width1, width2)
    img1_resized = cv2.resize(img1, (new_width, new_height))
    img2_resized = cv2.resize(img2, (new_width, new_height))

    # 将图片转换为灰度图
    gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

    # 计算差异
    diff = cv2.absdiff(gray1, gray2)

    # 设置阈值以高亮显示差异
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 用矩形框将差异区域框起来
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img1_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.rectangle(img2_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 调整显示尺寸
    display_scale = 0.3
    img1_display = cv2.resize(img1_resized, (int(new_width * display_scale), int(new_height * display_scale)))
    img2_display = cv2.resize(img2_resized, (int(new_width * display_scale), int(new_height * display_scale)))

    # 并排显示输入图片和结果图片
    combined = np.hstack((img1_display, img2_display))
    cv2.imshow("Comparison", combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 使用示例
compare_images(r"C:\Users\Admin\Pictures\1.jpg", r"C:\Users\Admin\Pictures\2.jpg")