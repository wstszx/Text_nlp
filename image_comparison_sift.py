import cv2
import numpy as np

def compare_images_sift(image_path1, image_path2):
    # 读取两张图片
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    # 将图片转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 创建SIFT对象
    sift = cv2.SIFT_create()

    # 提取关键点和描述符
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    # 创建BFMatcher对象
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    # 匹配描述符
    matches = bf.match(des1, des2)

    # 进行比例测试
    good_matches = []
    for m in matches:
        if len(good_matches) < 4:
            good_matches.append(m)
        else:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # 计算匹配数量
            mask_matches = mask.ravel().tolist()
            match_count = mask_matches.count(1)

            if match_count > 3:
                good_matches.append(m)

    # 计算两张图片是否内容相同
    if len(good_matches) / len(matches) > 0.8:
        print("两张图片内容相同")
    else:
        print("两张图片内容不同")

    # 对img1和img2进行高度调整
    height = min(img1.shape[0], img2.shape[0])
    img1_resized = cv2.resize(img1, (int(img1.shape[1] * height / img1.shape[0]), height))
    img2_resized = cv2.resize(img2, (int(img2.shape[1] * height / img2.shape[0]), height))

    # 添加间距
    spacing_width = 50
    spacing = np.zeros((height, spacing_width, 3), dtype=np.uint8)
    result = np.concatenate((img1_resized, spacing, img2_resized), axis=1)

    # 根据关键点绘制匹配结果
    result_drawn = cv2.drawMatches(img1_resized, kp1, img2_resized, kp2, good_matches, result, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # 显示结果
    display_scale = 0.3
    height, width = result.shape[:2]
    result_display = cv2.resize(result_drawn, (int(width * display_scale), int(height * display_scale)))
    cv2.imshow("SIFT Comparison", result_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 使用示例
compare_images_sift(r"C:\Users\Admin\Pictures\7.jpg", r"C:\Users\Admin\Pictures\9.jpg")
