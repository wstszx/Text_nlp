import cv2
import numpy as np

# 定义np.hstack_pad函数
def hstack_pad(tup):
    # 获取最大高度
    max_height = max(im.shape[0] for im in tup)
    # 创建一个空列表
    padded_imgs = []
    # 遍历每个图片
    for im in tup:
        # 获取图片的高度和宽度
        h, w = im.shape[:2]
        # 创建一个全零数组，形状为最大高度和图片宽度
        shape = list(im.shape)
        shape[0] = max_height - h
        shape[1] = w
        # 在数组下方填充零值
        pad = np.zeros(shape, dtype=im.dtype)
        # 将原图片和填充后的数组垂直拼接
        padded_imgs.append(np.vstack((im, pad)))
    # 返回水平拼接后的结果
    return np.hstack(padded_imgs)

# 读取大图和小图
small_img = cv2.imread(r"C:\Users\Admin\Pictures\slide_.png") 
big_img = cv2.imread(r"verification_code\slide_auth.png")
# big_img = cv2.imread(r"verification_code\auth_code_big.png")
# small_img = cv2.imread(r"verification_code\auth_code_small.png") 

# 转换为RGB格式
big_img = cv2.cvtColor(big_img, cv2.COLOR_BGR2RGB)
small_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

# 获取小图轮廓
small_gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
ret, small_thresh = cv2.threshold(small_gray, 127, 255, 0)  
small_contours, hierarchy = cv2.findContours(small_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
small_cnt = small_contours[0]

# 提取小图轮廓特征
small_cnt_features = cv2.HuMoments(cv2.moments(small_cnt)).flatten()  

# 在大图上搜索
big_gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
ret, big_thresh = cv2.threshold(big_gray, 127, 255, 0)
big_contours, hierarchy = cv2.findContours(big_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in big_contours:
    # 计算大图轮廓特征
    cnt_features = cv2.HuMoments(cv2.moments(cnt)).flatten()
    
    # 比较两轮廓特征距离
    dist = np.linalg.norm(small_cnt_features - cnt_features)
    print(dist)
    # 找到相似轮廓 
    if dist < 0.01:
        x,y,w,h = cv2.boundingRect(cnt)
        cv2.rectangle(big_img,(x,y),(x+w,y+h),(0,255,0),2)
        print("Similar Contour Top Left: ", (x, y))
        
# 使用np.hstack_pad函数拼接大图和小图
vis = hstack_pad((small_img, big_img)) 

# 显示
cv2.imshow('Match Result', vis)
cv2.waitKey(0)
cv2.destroyAllWindows()
