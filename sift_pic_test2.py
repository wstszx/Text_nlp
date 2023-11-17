# 导入所需的库
import cv2
import numpy as np

# 读取大图和小图
# big_image = cv2.imread("big.jpg")
# small_image = cv2.imread("small.jpg")
# big_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth1.png")
# small_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small2.png")
big_image = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\i002.jpg")
small_image = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\t003.jpg")
# 获取小图的宽度和高度
w, h = small_image.shape[:2]

# 使用ORB算法进行特征匹配
orb = cv2.ORB_create()
kp1, des1 = orb.detectAndCompute(big_image, None)
kp2, des2 = orb.detectAndCompute(small_image, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)

# 找到最佳匹配的位置
best_match = matches[0]
x1, y1 = kp1[best_match.queryIdx].pt
x2, y2 = kp2[best_match.trainIdx].pt
dx, dy = x1 - x2, y1 - y2

# 在大图上画出矩形框
cv2.rectangle(big_image, (int(dx), int(dy)), (int(dx + w), int(dy + h)), (0, 255, 0), 3)

# 调整图片大小为400x700，并显示结果
big_image = cv2.resize(big_image, (400, 700))
cv2.imshow("Result", big_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
