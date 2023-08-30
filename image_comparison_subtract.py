import cv2
import numpy as np

# 读取两张图片
img1 = cv2.imread(r"C:\Users\Admin\Pictures\7.jpg")
img2 = cv2.imread(r"C:\Users\Admin\Pictures\9.jpg")

# 获取两张图片的高度和宽度
h1, w1 = img1.shape[:2]
h2, w2 = img2.shape[:2]

# 如果两张图片的大小不一致，需要先调整到相同的大小
if h1 != h2 or w1 != w2:
    # 以较小的高度和宽度为标准，对较大的图片进行裁剪
    h = min(h1, h2)
    w = min(w1, w2)
    img1 = img1[:h, :w]
    img2 = img2[:h, :w]

# 使用subtract函数对两张图片进行减法运算
difference = cv2.subtract(img1, img2)

# 如果结果是全零的，说明两张图片完全相同
result = not np.any(difference)
if result:
    print("两张图片一样")
else:
    # 保存差异图像
    cv2.imwrite("difference.jpg", difference)
    print("两张图片不一样")
