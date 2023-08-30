# 导入segment_anything模块
from segment_anything import SamPredictor, sam_model_registry

# 创建一个模型实例，指定模型类型和检查点路径
sam = sam_model_registry["sam"] (checkpoint="path/to/checkpoint")
predictor = SamPredictor (sam)

# 读取输入图像，这里使用opencv-python模块
import cv2
image = cv2.imread (r"D:\AI\images\train\.trashed-1675415769-1672815101675.jpg")

# 设置输入图像
predictor.set_image (image)

# 定义输入提示，这里使用一个点来指示要分割的对象
input_prompts = [{"type": "point", "x": 100, "y": 200}]

# 生成掩码，返回一个字典，包含掩码、类别和分数
masks, classes, scores = predictor.predict (input_prompts)

# 对掩码进行后处理，这里使用pycocotools模块
from pycocotools import mask as mask_utils
masks = mask_utils.decode (masks)

# 保存掩码为png格式，这里使用matplotlib模块
import matplotlib.pyplot as plt
plt.imsave ("path/to/output", masks[0])
