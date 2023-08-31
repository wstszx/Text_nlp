import ddddocr
import subprocess
import cv2

ocr = ddddocr.DdddOcr(beta=True)

# subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])
# subprocess.run(["adb", "pull", "/sdcard/screen.png", "."])

with open(r'D:\python\Text_nlp\verification_code\code.png', 'rb') as f:
    image_bytes = f.read()

res = ocr.classification(image_bytes)
print(res)



# det = ddddocr.DdddOcr(det=True)

# with open(r'D:\python\Text_nlp\verification_code\code.png', 'rb') as f:
#     image = f.read()

# poses = det.detection(image)
# print(poses)

# im = cv2.imread(r'D:\python\Text_nlp\verification_code\code.png')

# for box in poses:
#     x1, y1, x2, y2 = box
#     im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)

# cv2.imwrite("result.jpg", im)
