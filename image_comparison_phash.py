import cv2
import numpy as np

def pHash(img, leng=32, wid=32):
    # 缩放尺寸
    # img = cv2.resize(img, (leng, wid))
    # 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 计算DCT
    dct = cv2.dct(np.float32(gray))
    # 选取左上角8*8的矩阵
    dct_roi = dct[0:8, 0:8]
    # 计算DCT均值
    avreage = np.mean(dct_roi)
    # 计算哈希值
    phash_01 = (dct_roi > avreage) + 0
    phash_list = phash_01.reshape(1, -1)[0].tolist()
    hash = ''.join([str(x) for x in phash_list])
    return hash

def Hamming_distance(hash1, hash2):
    # 计算汉明距离
    num = 0
    for index in range(len(hash1)):
        if hash1[index] != hash2[index]:
            num += 1
    return num

if __name__ == '__main__':
    image1 = cv2.imread(r"C:\Users\Admin\Pictures\7.jpg")
    image2 = cv2.imread(r"C:\Users\Admin\Pictures\8.jpg")
    
    # 计算pHash指纹
    p_hash1 = pHash(image1)
    p_hash2 = pHash(image2)
    
    # 计算汉明距离
    p_dist = Hamming_distance(p_hash1, p_hash2)
    
    print('p_dist is %d' % p_dist + ', similarity is %f' % (1 - p_dist * 1.0 / 64))
