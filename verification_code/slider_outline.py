# 导入模块
import cv2
import numpy as np

# 读取大图和小图
big_image = r"verification_code\slide_auth.png"
small_image = r"C:\Users\Admin\Pictures\slide_.png"
big_img = cv2.imread(big_image)
small_img = cv2.imread(small_image)

# 转换为灰度图
big_gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
small_gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)

# 二值化
_, big_thresh = cv2.threshold(big_gray, 127, 255, cv2.THRESH_BINARY)
_, small_thresh = cv2.threshold(small_gray, 127, 255, cv2.THRESH_BINARY)

# 查找轮廓
big_contours, _ = cv2.findContours(big_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 修改这一行
small_contours, _ = cv2.findContours(small_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 修改这一行

# 取小图的第一个轮廓作为模板
template = small_contours[0]

# 定义一个空列表，用于存储匹配结果
matches = []

# 遍历大图的所有轮廓，计算与模板的匹配度
for contour in big_contours:
    # 使用cv2.matchShapes()函数，方法为1，参数为0
    match = cv2.matchShapes(template, contour, 1, 0.0)
    # 将匹配度和轮廓添加到列表中
    matches.append((match, contour))

# 对列表按照匹配度从小到大排序
matches.sort(key=lambda x: x[0])

# 取列表中前两个元素，即最相似的两个轮廓
best_matches = matches[:2]

# 在大图上绘制矩形框，颜色为红色，线宽为3像素
for _, contour in best_matches:
    # 计算轮廓的最小外接矩形
    x, y, w, h = cv2.boundingRect(contour)
    # 使用cv2.rectangle()函数绘制矩形框
    cv2.rectangle(big_img, (x, y), (x + w, y + h), (0, 0, 255), 3)

# 显示结果图像
cv2.imshow("Result", big_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
