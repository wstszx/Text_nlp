# 导入所需的库
import cv2
import numpy as np

# 读取大图和小图
# big_image = cv2.imread("big.jpg")
# small_image = cv2.imread("small.jpg")
# small_image = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\t003.jpg") # 小图
# big_image = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\i002.jpg") # 大图
# big_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth1.png")
# small_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small2.png")
small_image = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145521.png") # 小图
big_image = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145457.jpg") # 大图

# 定义一个函数，用于在大图中画出小图的位置
def draw_rectangle(image, top_left, bottom_right, color, thickness):
    # 画出矩形框
    cv2.rectangle(image, top_left, bottom_right, color, thickness)
    image = cv2.resize(image, (400, 700)) 
    # 显示图片
    cv2.imshow("Result", image)
    # 等待按键
    cv2.waitKey(0)
    # 关闭窗口
    cv2.destroyAllWindows()

# 定义一个函数，用于进行多尺度模板匹配
def MultiScaleTemplateMatchingPre(big_image, small_image):
    # 获取小图的宽度和高度
    w, h = small_image.shape[:2]
    # 定义一个列表，用于存储不同尺度的结果
    results = []
    # 遍历不同的缩放比例
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # 缩放大图
        resized = cv2.resize(big_image, (int(big_image.shape[1] * scale), int(big_image.shape[0] * scale)))
        # 计算缩放比例
        ratio = big_image.shape[1] / float(resized.shape[1])
        # 如果缩放后的大图比小图还小，就跳出循环
        if resized.shape[0] < h or resized.shape[1] < w:
            break
        # 进行模板匹配
        result = cv2.matchTemplate(resized, small_image, cv2.TM_CCOEFF_NORMED)
        # 获取最佳匹配的位置和相似度
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # 将结果添加到列表中
        results.append((max_val, max_loc, ratio))
    # 对结果按相似度降序排序
    results.sort(key=lambda x: x[0], reverse=True)
    # 返回最佳的结果
    return results[0]

# 定义一个函数，用于进行模板匹配
def TemplateMatching(big_image, small_image):
    # 进行模板匹配
    result = cv2.matchTemplate(big_image, small_image, cv2.TM_CCOEFF_NORMED)
    # 获取最佳匹配的位置和相似度
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 返回结果
    return max_val, max_loc

# 定义一个函数，用于进行SURF特征匹配
def SIFTMatching(big_image, small_image):
    # 创建SIFT特征提取器
    sift = cv2.SIFT_create()
    # 提取大图和小图的特征点和描述符
    kp1, des1 = sift.detectAndCompute(big_image, None)
    kp2, des2 = sift.detectAndCompute(small_image, None)
    # 创建FLANN匹配器
    flann = cv2.FlannBasedMatcher(dict(algorithm=0, trees=5), dict(checks=50))
    # 进行特征匹配
    matches = flann.knnMatch(des1, des2, k=2)
    # 筛选出好的匹配点，使用Lowe's ratio test
    good_matches = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
    # 如果好的匹配点数量大于4，就计算变换矩阵，并找到小图在大图中的位置
    if len(good_matches) > 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = small_image.shape[:2]
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        # 返回结果
        return len(good_matches), dst
    else:
        # 返回空结果
        return None, None

# 定义一个函数，用于进行BRISK特征匹配
def BRISKMatching(big_image, small_image):
    # 创建BRISK特征提取器
    brisk = cv2.BRISK_create()
    # 提取大图和小图的特征点和描述符
    kp1, des1 = brisk.detectAndCompute(big_image, None)
    kp2, des2 = brisk.detectAndCompute(small_image, None)
    # 创建BF匹配器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # 进行特征匹配
    matches = bf.match(des1, des2)
    # 对匹配点按距离升序排序
    matches.sort(key=lambda x: x.distance)
    # 筛选出好的匹配点，使用距离阈值
    good_matches = []
    for m in matches:
        if m.distance < 50:
            good_matches.append(m)
    # 如果好的匹配点数量大于4，就计算变换矩阵，并找到小图在大图中的位置
    if len(good_matches) > 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = small_image.shape[:2]
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        # 返回结果
        return len(good_matches), dst
    else:
        # 返回空结果
        return None, None

# 调用MultiScaleTemplateMatchingPre算法，进行图像识别
similarity_1, location_1, ratio_1 = MultiScaleTemplateMatchingPre(big_image, small_image)
# 计算小图在大图中的位置，考虑缩放比例
top_left_1 = (int(location_1[0] * ratio_1), int(location_1[1] * ratio_1))
bottom_right_1 = (int((location_1[0] + small_image.shape[1]) * ratio_1), int((location_1[1] + small_image.shape[0]) * ratio_1))
# 在大图中画出小图的位置，使用红色矩形框，线宽为3
draw_rectangle(big_image.copy(), top_left_1, bottom_right_1, (0, 0, 255), 3)

# 调用TemplateMatching算法，进行图像识别
similarity_2, location_2 = TemplateMatching(big_image.copy(), small_image.copy())
# 计算小图在大图中的位置
top_left_2 = location_2
bottom_right_2 = (location_2[0] + small_image.shape[1], location_2[1] + small_image.shape[0])
# 在大图中画出小图的位置，使用绿色矩形框，线宽为3
draw_rectangle(big_image.copy(), top_left_2, bottom_right_2, (0, 255, 0), 3)

# 调用SURFMatching算法，进行图像识别
matches_num_3, location_3 = SIFTMatching(big_image.copy(), small_image.copy())
# 如果有结果，就在大图中画出小图的位置，使用蓝色矩形框，线宽为3
if location_3 is not None:
    draw_rectangle(big_image.copy(), tuple(location_3[0][0]), tuple(location_3[2][0]), (255,0, 0), 3)
# 调用BRISKMatching算法，进行图像识别
matches_num_4, location_4 = BRISKMatching(big_image.copy(), small_image.copy())

# 如果有结果，就在大图中画出小图的位置，使用黄色矩形框，线宽为3
if location_4 is not None: draw_rectangle(big_image.copy(), tuple(location_4[0][0]), tuple(location_4[2][0]), (0, 255, 255), 3)

# # 将大图和小图按照400x700的分辨率展示
# big_image = cv2.resize(big_image, (400, 700)) 
# small_image = cv2.resize(small_image, (400, 700)) 
# cv2.imshow('Big Image', big_image) 
# cv2.imshow('Small Image', small_image) 
# cv2.waitKey(0) 
# cv2.destroyAllWindows()    