# 导入cv2和numpy模块
import cv2
import numpy as np

# 定义常量
BIG_IMAGE = r"verification_code\slide_auth1.png" # 大图路径
SMALL_IMAGE = r"verification_code\slide_auth_small1.png" # 小图路径
# BIG_IMAGE = r"verification_code\slide_auth.png" # 大图路径
# SMALL_IMAGE = r"verification_code\slide_auth_small.png" # 小图路径
THRESHOLD = 0.9 # 匹配阈值
FIND_NUM = 2 # 匹配个数

# 定义边缘检测函数
def edge_detection(image):
    # 将图像转换为灰度图
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 使用Canny算法进行边缘检测
    img_edge = cv2.Canny(img_gray, 100, 200)
    return img_edge

# 定义模板匹配函数
def template_matching(big_img_edge, small_img_edge):
    # 使用相关系数归一化方法进行模板匹配
    res = cv2.matchTemplate(big_img_edge, small_img_edge, cv2.TM_CCOEFF_NORMED) 
    # 获取最高的FIND_NUM个匹配索引
    idx_1d = np.argpartition(res.flatten(), -FIND_NUM)[-FIND_NUM:]
    # 转换为二维坐标
    idx_2d = np.unravel_index(idx_1d, res.shape)
    return idx_2d

# 读取大图和小图
big_img = cv2.imread(BIG_IMAGE) 
small_img = cv2.imread(SMALL_IMAGE)

# 对大图和小图进行边缘检测
big_img_edge = edge_detection(big_img)
small_img_edge = edge_detection(small_img)

# 对大图进行模板匹配，找出匹配小图的区域坐标
x_list, y_list = template_matching(big_img_edge, small_img_edge)

# 获取小图的高度和宽度
h, w = small_img_edge.shape

previous_center_x = None
# 在大图上画出匹配区域的矩形框
for y, x in zip(x_list, y_list):
    center_x = x + w / 2
    center_y = y + h / 2
    print("Center point coordinates: ({}, {})".format(center_x, center_y))
    if previous_center_x is not None: # 检查是否是第一个点
        distance_x = abs(center_x - previous_center_x) # 计算两个点在x方向的距离
        print("Distance in x direction: {}".format(distance_x))
    
    previous_center_x = center_x # 存储当前点的x坐标作为前一个点的x坐标
    cv2.rectangle(big_img, (x, y), (x+w, y+h), (0, 0, 255), 2)

# 显示结果图像，并等待按键关闭窗口
cv2.imshow('Detected', big_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
