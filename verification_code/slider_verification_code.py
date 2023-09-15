# 导入 ddddocr 和 PIL 库
import ddddocr
from PIL import Image, ImageDraw

# 创建一个 DdddOcr 对象
det = ddddocr.DdddOcr(det=False, ocr=False)
small_img = r"verification_code\slide_auth_small.png"
big_img = r"verification_code\slide_auth.png"
# 打开两张图片，并将它们转换为字节对象
with open(small_img, 'rb') as f:
    target_bytes = f.read()

with open(big_img, 'rb') as f:
    background_bytes = f.read()

# 使用 slide_match 方法来计算小图片在大图片中的位置，并打印结果
res = det.slide_match(target_bytes, background_bytes, simple_target=True)

print(res)

# 使用 PIL 库来打开两张图片，并在大图片上绘制一个红色的矩形框，表示小图片的位置
target_img = Image.open(small_img)
background_img = Image.open(big_img)

x1, y1, x2, y2 = res['target']
draw = ImageDraw.Draw(background_img)
draw.rectangle((x1, y1, x2, y2), outline='red')

# 创建一个新的空白图片，宽度为两张图片的宽度之和，高度为两张图片中较大的高度
new_width = target_img.width + background_img.width
new_height = max(target_img.height, background_img.height)
new_img = Image.new('RGB', (new_width, new_height))

# 将两张图片粘贴到新图片上，小图片在左边，大图片在右边
new_img.paste(target_img, (0, 0))
new_img.paste(background_img, (target_img.width, 0))

# 使用 PIL 库的 show 方法来显示新图片
new_img.show()
