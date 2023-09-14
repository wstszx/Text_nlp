import cv2
import numpy as np

# 读取大图和小图
big_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth.png")
small_image = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small.png") 

# 获取小图的轮廓
small_gray = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
ret, small_thresh = cv2.threshold(small_gray, 127, 255, 0)
small_contours, hierarchy = cv2.findContours(small_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
small_contour = small_contours[0]

# 在大图中查找匹配轮廓的区域
results = []
big_gray = cv2.cvtColor(big_image, cv2.COLOR_BGR2GRAY)
ret, big_thresh = cv2.threshold(big_gray, 127, 255, 0)
big_contours, hierarchy = cv2.findContours(big_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for big_contour in big_contours:
    match = cv2.matchShapes(small_contour, big_contour, 1, 0.0)
    if match < 0.15:
        results.append(big_contour)

# 画出匹配区域
matching_image = big_image.copy()
cv2.drawContours(matching_image, results, -1, (0,255,0), 2)
cv2.imwrite('output.jpg', matching_image)