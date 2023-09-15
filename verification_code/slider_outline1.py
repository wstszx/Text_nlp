import cv2
import numpy as np

big_image = r"verification_code\slide_auth.png"
small_image = r"C:\Users\Admin\Pictures\slide_.png"

img1 = cv2.imread(small_image) 
img2 = cv2.imread(big_image)

# 转换为灰度图
img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# 图像二值化
ret, thresh1 = cv2.threshold(img1_gray, 127, 255, cv2.THRESH_BINARY) 
ret, thresh2 = cv2.threshold(img2_gray, 127, 255, cv2.THRESH_BINARY)

# 寻找轮廓
contours1, hierarchy1 = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours2, hierarchy2 = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 计算每个轮廓的面积和周长
contours1_info = [(cv2.contourArea(c), cv2.arcLength(c, True)) for c in contours1]
contours2_info = [(cv2.contourArea(c), cv2.arcLength(c, True)) for c in contours2]

# 判断相似轮廓
similar_contours = []
for c1 in contours1_info:
    for c2 in contours2_info:
        if abs(c1[0] - c2[0]) < 100 and abs(c1[1] - c2[1]) < 100: 
            similar_contours.append((c1, c2))

# 在大图上画框            
for c1, c2 in similar_contours:
    x, y, w, h = cv2.boundingRect(contours2[contours2_info.index(c2)])
    cv2.rectangle(img2, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow('result', img2)
cv2.waitKey(0)
cv2.destroyAllWindows()