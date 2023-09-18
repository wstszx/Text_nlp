import cv2
import numpy as np

# 读取大图和小图
big_image = r"verification_code\slide_auth.png"
small_image = r"verification_code\slide_auth_small.png"
big_img = cv2.imread(big_image) 
small_img = cv2.imread(small_image)

# Canny边缘检测
big_img_gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
big_img_edge = cv2.Canny(big_img_gray, 100, 200)

small_img_gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
small_img_edge = cv2.Canny(small_img_gray, 100, 200)

# 模板匹配
res = cv2.matchTemplate(big_img_edge, small_img_edge, cv2.TM_CCOEFF_NORMED) 
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

# 获取匹配区域坐标并画矩形框
x, y = max_loc
h, w = small_img_edge.shape
cv2.rectangle(big_img, (x, y), (x+w, y+h), (0, 0, 255), 2)

cv2.imshow('Detected', big_img)
cv2.waitKey(0)
cv2.destroyAllWindows()