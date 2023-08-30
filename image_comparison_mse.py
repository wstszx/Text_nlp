from PIL import Image, ImageChops, ImageOps

# 计算两张图片之间均方差（Mean Square Error）
def mse(image1, image2):
    # 如果两幅图像大小不同，则将其调整为相同大小
    if image1.size != image2.size:
        image2 = ImageOps.fit(image2, image1.size)

    difference = ImageChops.difference(image1, image2)

    pixels = difference.getdata()

    # 累加所有RGB通道之间差异平方和
    total = sum([sum(map(lambda x: x * x, pixel)) for pixel in pixels])

    # 返回total除以总像素数n得到MSE值。
    return total / float(len(pixels))


# 加载第一张图像
image_1_path = r"C:\Users\Admin\Pictures\7.jpg"
image_1_obj = Image.open(image_1_path).convert("RGB")

# 加载第二张图像
image_2_path = r"C:\Users\Admin\Pictures\8.jpg"
image_2_obj = Image.open(image_2_path).convert("RGB")

mse_value = mse(image_1_obj, image_2_obj)

if mse_value == 0.0:
    print('这两张图片内容相同')
else:
    print('这两张图片内容不同')
