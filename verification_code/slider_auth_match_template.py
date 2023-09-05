# 导入必要的库
import cv2
import numpy as np

# 读取大图和小图
big_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth.png")
small_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small.png")

# 获取小图的宽度和高度
w, h = small_image.shape[:2]

# 第一步：使用模板匹配找到与小图完全相同的元素
# 使用cv2.TM_CCOEFF_NORMED方法计算匹配矩阵
result = cv2.matchTemplate(big_image, small_image, cv2.TM_CCOEFF_NORMED)
# 获取匹配矩阵中的最大值和最小值及其位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
# 如果最大值大于阈值（0.9），则认为找到了匹配的元素
threshold = 0.9
if max_val >= threshold:
    # 计算匹配元素的左上角和右下角坐标
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    # 在大图上画出矩形框，并打印左上角坐标
    cv2.rectangle(big_image, top_left, bottom_right, (0, 0, 255), 2)
    print('The top-left coordinate of the exact match is:', top_left)
else:
    print('No exact match found.')

# 第二步：使用轮廓检测找到与小图轮廓相似的元素
# 将大图和小图转换为灰度图
big_gray = cv2.cvtColor(big_image, cv2.COLOR_BGR2GRAY)
small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
# 使用Otsu's方法对灰度图进行二值化
_, big_thresh = cv2.threshold(big_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
_, small_thresh = cv2.threshold(small_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# 找到大图和小图的轮廓
big_contours, _ = cv2.findContours(big_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
small_contour, _ = cv2.findContours(small_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
# 遍历大图的轮廓，计算与小图轮廓的形状匹配度
min_diff = np.inf # 初始化最小差异为无穷大
best_cnt = None # 初始化最佳轮廓为None
for cnt in big_contours:
    # 使用cv2.CONTOURS_MATCH_I3方法计算形状匹配度
    diff = cv2.matchShapes(small_contour, cnt, cv2.CONTOURS_MATCH_I3, 0.0)
    # 如果差异小于最小差异，更新最小差异和最佳轮廓
    if diff < min_diff:
        min_diff = diff
        best_cnt = cnt
# 如果最小差异小于阈值（0.1），则认为找到了相似的元素
threshold = 0.1
if min_diff <= threshold:
    # 计算相似元素的外接矩形的左上角和右下角坐标
    x, y, w, h = cv2.boundingRect(best_cnt)
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    # 在大图上画出矩形框，并打印左上角坐标
    cv2.rectangle(big_image, top_left, bottom_right, (0, 255, 0), 2)
    print('The top-left coordinate of the similar match is:', top_left)
else:
    print('No similar match found.')

# 显示最终的大图
cv2.imshow('Result', big_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
