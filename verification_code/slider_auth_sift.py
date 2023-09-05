# 导入必要的库
import cv2
import numpy as np

# 导入SIFT函数
sift = cv2.SIFT_create()

# 读取大图和小图
big_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth.png")
small_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small.png")

# 获取小图的宽度和高度
w, h = small_image.shape[:2]

# 第一步：使用SIFT特征匹配找到与小图相同的元素
# 将大图和小图转换为灰度图
big_gray = cv2.cvtColor(big_image, cv2.COLOR_BGR2GRAY)
small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)

# 使用SIFT对象检测和计算大图和小图中的关键点和描述符
keypoints_1, descriptors_1 = sift.detectAndCompute(big_gray, None)
keypoints_2, descriptors_2 = sift.detectAndCompute(small_gray, None)

# 使用FLANN匹配器进行快速匹配
index_params = dict(algorithm=0, trees=5)
search_params = dict()
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(descriptors_1, descriptors_2, k=2)

# 选择最佳的匹配结果
good_points = []
ratio = 0.6
for m, n in matches:
    if m.distance < ratio * n.distance:
        good_points.append(m)

# 如果有足够多的好的匹配结果，则认为找到了相同的元素
MIN_MATCH_COUNT = 10
if len(good_points) > MIN_MATCH_COUNT:
    # 获取相同元素在大图和小图中的坐标
    src_pts = np.float32([keypoints_1[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints_2[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)
    # 计算相同元素的仿射变换矩阵
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    # 计算相同元素在大图中的外接矩形的四个顶点坐标
    h, w = small_gray.shape
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)
    # 在大图上画出矩形框，并打印左上角坐标
    cv2.polylines(big_image, [np.int32(dst)], True, (0, 0, 255), 2)
    print('The top-left coordinate of the exact match is:', dst[0][0])
else:
    print('No exact match found.')

# 在大图上画出与小图匹配的特征点
result = cv2.drawMatches(big_image, keypoints_1, small_image, keypoints_2, good_points, None)

# 显示最终的大图
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
