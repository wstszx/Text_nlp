import cv2
import numpy as np

# 读取图片  
small_image = r"C:\Users\Admin\Pictures\slide_.png"
big_image = r"verification_code\slide_auth.png"

img1 = cv2.imread(small_image)
img2 = cv2.imread(big_image)

# 转灰度图
img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# SIFT特征检测
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1_gray, None)
kp2, des2 = sift.detectAndCompute(img2_gray, None)

# 特征匹配  
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# 按Lowe比率获得优质匹配
good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append(m)

# 找到两个不同的匹配区域
regions = []
if len(good) > 4:
    # 第一个匹配区域
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good[:4]]).reshape(-1,1,2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good[:4]]).reshape(-1,1,2)
    
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    matches = good[4:]
    
    h, w = img1_gray.shape  
    pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts,M)
    regions.append(dst)

    # 第二个匹配区域 
    if len(matches) > 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches[:4]]).reshape(-1,1,2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches[:4]]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        h, w = img1_gray.shape
        pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        regions.append(dst)
        
# 绘制矩形
for region in regions:
    img2 = cv2.polylines(img2,[np.int32(region)],True,(255,0,0),2, cv2.LINE_AA) 
    
# 显示结果
cv2.imshow("matched", img2)
cv2.waitKey()
cv2.destroyAllWindows()