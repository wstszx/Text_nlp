import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import cv2
import supervision as sv

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_h"
CHECK_POINT = 'sam_vit_h_4b8939.pth'

# 加载模型
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECK_POINT).to(device=DEVICE)

# 预测分割
mask_generator = SamAutomaticMaskGenerator(sam)

image_bgr = cv2.imread(r"D:\AI\images\train\Screenshot_2023-01-04-17-07-52-807_com.jifen.qukan.jpg")
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

sam_result = mask_generator.generate(image_rgb)

# 创建一个图像的副本
image_copy = image_bgr.copy()

# 遍历每个分割结果
for result in sam_result:
  # 获取掩码的边界框
  bbox = result['bbox']
  print(bbox)
  # 将xywh格式转换为xyxy格式
  x1, y1, x2, y2 = bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]
  # 在图像上绘制一个红色矩形
  cv2.rectangle(image_copy, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

# 使用sv模块的plot_images_grid方法，将原始图像和绘制矩形的图像并排显示在一个网格中，方便比较。
sv.plot_images_grid(
    images=[image_bgr, image_copy],
    grid_size=(1, 2),
    titles=['source image', 'image with rectangles']
)  




