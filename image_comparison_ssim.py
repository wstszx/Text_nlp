from skimage.metrics import structural_similarity as ssim
import cv2

def compare_images(imageA, imageB):
    # 将图像转换为灰度
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # 调整图像B的大小与图像A相同
    grayB = cv2.resize(grayB, (grayA.shape[1], grayA.shape[0]))

    # 计算SSIM
    score = ssim(grayA, grayB)

    return score

# 读取两个图像
imageA = cv2.imread(r"C:\Users\Admin\Pictures\7.jpg")
imageB = cv2.imread(r"C:\Users\Admin\Pictures\9.jpg")

# 计算并打印SSIM
score = compare_images(imageA, imageB)
print("Image similarity:", score)
