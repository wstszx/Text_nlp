import cv2
import numpy as np
import uiautomator2 as u2
import time
import os

# 连接设备
# d = u2.connect()

# 获取截图
# screenshot = d.screenshot(format="opencv")

# 将截图转换为OpenCV格式
# img2 = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# 读取图片
# img1 = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145521.png") # 小图
# img2 = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145457.jpg") # 大图
# img1 = cv2.imread(os.path.join("C:", "Users", "Admin", "Downloads", "Screenshot_part.png")) # 小图
# img2 = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_full.jpg") # 大图
# img2 = cv2.imread(r"C:\Users\Admin\Downloads\pinduoduo_pad_full.png") # 大图
# img1 = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\t003.jpg") # 小图
# img2 = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\i002.jpg") # 大图
small_image = r"C:\Users\Admin\Pictures\slide_.png"
big_image = r"verification_code\slide_auth.png"
img1 = cv2.imread(small_image) # 小图
img2 = cv2.imread(big_image) # 大图

# 标定相机并校正畸变
objpoints = []  # 三维点
imgpoints = []  # 二维点
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6 * 8, 3), np.float32)
objp[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2)
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
ret1, corners1 = cv2.findChessboardCorners(gray1, (8, 6), None)
ret2, corners2 = cv2.findChessboardCorners(gray2, (8, 6), None)
if ret1 and ret2:
    objpoints.append(objp)
    corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
    corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
    imgpoints.append(corners1)
    imgpoints.append(corners2)
    h1, w1 = gray1.shape[:2]
    h2, w2 = gray2.shape[:2]
    ret1, mtx1, dist1, rvecs1, tvecs1 = cv2.calibrateCamera(objpoints, imgpoints, (w1, h1), None, None)
    newcameramtx1, roi1 = cv2.getOptimalNewCameraMatrix(mtx1, dist1, (w1, h1), 1, (w1, h1))
    mapx1, mapy1 = cv2.initUndistortRectifyMap(mtx1, dist1, None, newcameramtx1, (w1, h1), 5)
    img1 = cv2.remap(img1, mapx1, mapy1, cv2.INTER_LINEAR)

    ret2, mtx2, dist2, rvecs2, tvecs2 = cv2.calibrateCamera(objpoints, imgpoints, (w2, h2), None, None)
    newcameramtx2, roi2 = cv2.getOptimalNewCameraMatrix(mtx2, dist2, (w2, h2), 1, (w2, h2))
    mapx2, mapy2 = cv2.initUndistortRectifyMap(mtx2, dist2, None, newcameramtx2, (w2, h2), 5)
    img2 = cv2.remap(img2, mapx2, mapy2, cv2.INTER_LINEAR)

# 转换为灰度图
img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# 创建一个SIFT对象
sift = cv2.SIFT_create()

# 检测并计算关键点和描述符
kp1, des1 = sift.detectAndCompute(img1_gray, None)
kp2, des2 = sift.detectAndCompute(img2_gray, None)

# 创建一个BFMatcher对象
bf = cv2.BFMatcher()

# 为每个关键点找到k个最佳匹配
matches = bf.knnMatch(des1, des2, k=2)

# 应用比值测试来选择只有好的匹配
good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append(m)

# 绘制好的匹配
img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

# 从匹配中提取出对应点对
src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

# 计算单应性矩阵
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# 使用单应性矩阵将小图变换到大图上
h, w = img1_gray.shape
pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
dst = cv2.perspectiveTransform(pts, H)

# 绘制变换后的小图在大图上的位置
cv2.polylines(img2, [np.int32(dst)], True, (0, 0, 255), 3, cv2.LINE_AA)

# 计算矩形中心点坐标
x, y, w, h = cv2.boundingRect(np.int32(dst))
center_x, center_y = x + w//2, y + h//2

# 将矩形中心点用红色点绘制在图片上
cv2.circle(img2, (center_x, center_y), 5, (0, 0, 255), -1)

# 打印矩形中心点坐标
print("矩形中心点坐标: ({}, {})".format(center_x, center_y))
# 点击矩形中心点
# time.sleep(5)
# d.click(center_x, center_y)

# 计算准确率
accuracy = len(good) / len(matches) * 100
print("准确率：{:.2f}%".format(accuracy))

# 显示结果
# Get the size of the larger image
h, w = img2.shape[:2]
cv2.namedWindow("img3", cv2.WINDOW_NORMAL)
cv2.resizeWindow("img3", w, h)
cv2.imshow("img3", img3)
cv2.namedWindow("img2", cv2.WINDOW_NORMAL)
cv2.resizeWindow("img2", w, h)
cv2.imshow("img2", img2)
cv2.waitKey(0)
cv2.destroyAllWindows()
