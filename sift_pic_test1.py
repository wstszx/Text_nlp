import cv2
import numpy as np

# 读取图片
img_big = cv2.imread('big.jpg')
img_small = cv2.imread('small.jpg') 
# img_big = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth1.png")
# img_small = cv2.imread(r"C:\Users\Admin\Pictures\slide_auth_small2.png")
# img_small = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145521.png") # 小图
# img_big = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_20230515_145457.jpg") # 大图
# img_small = cv2.imread(os.path.join("C:", "Users", "Admin", "Downloads", "Screenshot_part.png")) # 小图
# img_big = cv2.imread(r"C:\Users\Admin\Downloads\Screenshot_full.jpg") # 大图
# img_big = cv2.imread(r"C:\Users\Admin\Downloads\pinduoduo_pad_full.png") # 大图
# img_small = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\t003.jpg") # 小图
# img_big = cv2.imread(r"C:\Users\Admin\Documents\WeChat Files\wstszx\FileStorage\File\2023-05\match\i002.jpg") # 大图

# 特征检测与描述
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img_small,None)
kp2, des2 = sift.detectAndCompute(img_big,None)

# 特征匹配
bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
matches = bf.match(des1,des2) 

# 筛选匹配点对
good_matches = []
for m in matches:
    if m.distance < 0.7*matches[0].distance:
        good_matches.append(m)

# 获取匹配点坐标
pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)

# RANSAC计算Homography
M, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC,5.0)

# 标注结果图片
h,w = img_small.shape[:2]
pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)  
dst = cv2.perspectiveTransform(pts,M)
img_out = cv2.polylines(img_big,[np.int32(dst)],True,(0,255,0),3)
print(dst)

# 修改窗口大小
cv2.namedWindow('result', cv2.WINDOW_NORMAL)  
cv2.resizeWindow('result', 400,700) 

# 计算矩形中心点坐标
x = (dst[0][0][0] + dst[1][0][0] + dst[2][0][0] + dst[3][0][0]) / 4
y = (dst[0][0][1] + dst[1][0][1] + dst[2][0][1] + dst[3][0][1]) / 4

# 在图片上绘制红色的点
img_out = cv2.circle(img_out, (int(x), int(y)), radius=5, color=(0, 0, 255), thickness=3)

cv2.imshow('result', img_out)
cv2.waitKey(0)
cv2.destroyAllWindows()