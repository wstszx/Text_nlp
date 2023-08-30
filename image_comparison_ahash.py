from PIL import Image, ImageFilter, ImageDraw
import numpy as np

def image_to_gray(image_path, size=(8, 8)):
    image = Image.open(image_path)
    image = image.resize(size, Image.LANCZOS)
    image = image.convert('L')
    return image

def ahash(image):
    pixels = np.asarray(image)
    mean = np.mean(pixels)
    diff = np.where(pixels > mean, 1, 0)
    hash_str = ''.join(str(x) for x in diff.flatten())
    return hash_str

def hamming_distance(hash1, hash2):
    return np.count_nonzero(hash1 != hash2)

def is_same_image(image_path1, image_path2, 
                  sizes=[(8, 8), (16, 16), (32, 32), (64, 64)], 
                  threshold=0):
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    if img1.size != img2.size:
        return False

    for size in sizes:
        gray1 = image_to_gray(image_path1, size).filter(ImageFilter.GaussianBlur(1))
        gray2 = image_to_gray(image_path2, size).filter(ImageFilter.GaussianBlur(1))
        hash1 = ahash(gray1)
        hash2 = ahash(gray2)
        distance = hamming_distance(hash1, hash2)
        if distance <= threshold:
            return True
    
    return False

def draw_rectangle(image, box, outline="red"):
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, outline=outline)
    return image

image_path1 = r"C:\Users\Admin\Pictures\7.jpg"
image_path2 = r"C:\Users\Admin\Pictures\8.jpg"

image1 = Image.open(image_path1)
image2 = Image.open(image_path2)

if is_same_image(image_path1, image_path2):
    print("这两张图片内容相同")
else:
    print("这两张图片内容不同")
    width = max(image1.width, image2.width)
    height = max(image1.height, image2.height)
    new_image = Image.new("RGB", (2 * width, height))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (width, 0))

    draw = ImageDraw.Draw(new_image)
    draw_rectangle(new_image, (0, 0, width - 1, height - 1))
    draw_rectangle(new_image, (width, 0, 2 * width - 1, height - 1))

    new_image.show()