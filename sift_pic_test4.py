# 导入所需的库
import cv2
import numpy as np

# 读取大图和小图
# big_image = cv2.imread("big.jpg")
# small_image = cv2.imread("small.jpg")
small_image = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145521.png") # 小图
big_image = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145457.jpg") # 大图

# 定义显示结果的函数
def show_result(image, title):
    # 调整图片大小为400x700
    resized_image = cv2.resize(image, (400, 700))
    # 显示图片
    cv2.imshow(title, resized_image)
    # 等待按键
    cv2.waitKey(0)
    # 销毁窗口
    cv2.destroyAllWindows()

# MultiScaleTemplateMatchingPre算法
def multi_scale_template_matching_pre(big_image, small_image):
    # 获取小图的宽和高
    small_width, small_height = small_image.shape[:2]
    # 定义缩放比例列表
    scales = [0.5, 0.75, 1, 1.25, 1.5]
    # 定义最佳匹配结果的变量
    best_match = None
    # 遍历缩放比例列表
    for scale in scales:
        # 根据缩放比例调整大图的大小
        resized_big_image = cv2.resize(big_image, (0, 0), fx=scale, fy=scale)
        # 获取调整后的大图的宽和高
        resized_width, resized_height = resized_big_image.shape[:2]
        # 如果调整后的大图比小图还小，就跳过这个缩放比例
        if resized_width < small_width or resized_height < small_height:
            continue
        # 使用模板匹配算法在调整后的大图中寻找小图
        result = cv2.matchTemplate(resized_big_image, small_image, cv2.TM_CCOEFF_NORMED)
        # 获取最佳匹配位置和相似度
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # 如果没有最佳匹配结果，或者当前的相似度比之前的更高，就更新最佳匹配结果
        if best_match is None or max_val > best_match[0]:
            best_match = (max_val, max_loc, scale)
    # 如果有最佳匹配结果，就返回相似度，位置和缩放比例，否则返回None
    if best_match is not None:
        return best_match[0], best_match[1], best_match[2]
    else:
        return None

# TemplateMatching算法
def template_matching(big_image, small_image):
    # 使用模板匹配算法在大图中寻找小图
    result = cv2.matchTemplate(big_image, small_image, cv2.TM_CCOEFF_NORMED)
    # 获取最佳匹配位置和相似度
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 返回相似度和位置
    return max_val, max_loc

# SIFTMatching算法
def sift_matching(big_image, small_image):
    # 创建SIFT特征提取器
    sift = cv2.SIFT_create()
    # 提取大图和小图的特征点和描述符
    big_keypoints, big_descriptors = sift.detectAndCompute(big_image, None)
    small_keypoints, small_descriptors = sift.detectAndCompute(small_image, None)
    # 创建FLANN匹配器
    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    # 使用FLANN匹配器进行特征点匹配，并保留最佳的50个匹配结果
    matches = flann.knnMatch(small_descriptors, big_descriptors, k=2)
    good_matches = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
            if len(good_matches) > 50:
                break
    # 如果匹配结果少于4个，就返回None
    if len(good_matches) < 4:
        return None
    # 获取匹配的特征点的坐标
    small_points = np.float32([small_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    big_points = np.float32([big_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    # 使用RANSAC算法计算单应性矩阵
    H, mask = cv2.findHomography(small_points, big_points, cv2.RANSAC, 5.0)
    # 获取小图的四个角点的坐标
    small_height, small_width = small_image.shape[:2]
    corners = np.float32([[0, 0], [0, small_height - 1], [small_width - 1, small_height - 1], [small_width - 1, 0]]).reshape(-1, 1, 2)
    # 使用单应性矩阵将小图的角点映射到大图中
    transformed_corners = cv2.perspectiveTransform(corners, H)
    # 计算映射后的角点的最小外接矩形
    x, y, w, h = cv2.boundingRect(transformed_corners)
    # 返回相似度和位置
    return len(good_matches) / len(matches), (x, y)

# BRISKMatching算法
def brisk_matching(big_image, small_image):
    # 创建BRISK特征提取器
    brisk = cv2.BRISK_create()
    # 提取大图和小图的特征点和描述符
    big_keypoints, big_descriptors = brisk.detectAndCompute(big_image, None)
    small_keypoints, small_descriptors = brisk.detectAndCompute(small_image, None)
    # 创建BF匹配器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # 使用BF匹配器进行特征点匹配，并保留最佳的50个匹配结果
    matches = bf.match(small_descriptors, big_descriptors)
    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = matches[:50]
    # 如果匹配结果少于4个，就返回None
    if len(good_matches) < 4:
        return None
    # 获取匹配的特征点的坐标
    small_points = np.float32([small_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    big_points = np.float32([big_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    # 使用RANSAC算法计算单应性矩阵
    H, mask = cv2.findHomography(small_points, big_points, cv2.RANSAC, 5.0)
    # 获取小图的四个角点的坐标
    small_height, small_width = small_image.shape[:2]
    corners = np.float32([[0, 0], [0, small_height - 1], [small_width - 1, small_height - 1], [small_width - 1, 0]]).reshape(-1, 1, 2)
    # 使用单应性矩阵将小图的角点映射到大图中
    transformed_corners = cv2.perspectiveTransform(corners, H)
    # 计算映射后的角点的最小外接矩形
    x, y, w, h = cv2.boundingRect(transformed_corners)
    # 返回相似度和位置
    return len(good_matches) / len(matches), (x,y)

# 定义绘制矩形框的函数
def draw_rectangle(image, location):
    # 获取位置信息
    print(f"location: {location}")
    x,y,w,h = location
    # 绘制矩形框，颜色为红色，线宽为3像素
    cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),3)
    # cv2.rectangle(image, top_left, bottom_right, color, thickness)

# 调用MultiScaleTemplateMatchingPre算法，在大图中找到小图，并绘制矩形框，显示结果
similarity_1, location_1, scale_1 = multi_scale_template_matching_pre(big_image, small_image)
draw_rectangle(big_image, location_1)
show_result(big_image, "MultiScaleTemplateMatchingPre")

# 调用TemplateMatching算法，在大图中找到小图，并绘制矩形框，显示结果
similarity_2, location_2 = template_matching(big_image, small_image)
draw_rectangle(big_image, location_2)
show_result(big_image, "TemplateMatching")

# 调用SIFTMatching算法，在大图中找到小图，并绘制矩形框，显示结果
similarity_3, location_3 = sift_matching(big_image, small_image)
draw_rectangle(big_image, location_3)
show_result(big_image, "SIFTMatching")

# 调用BRISKMatching算法，在大图中找到小图，并绘制矩形框，显示结果
similarity_4, location_4 = brisk_matching(big_image, small_image)
draw_rectangle(big_image, location_4)
show_result(big_image, "BRISKMatching")
