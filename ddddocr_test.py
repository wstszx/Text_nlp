import ddddocr
import subprocess

ocr = ddddocr.DdddOcr(beta=True)

# subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"])
# subprocess.run(["adb", "pull", "/sdcard/screen.png", "."])

with open('a.jpg', 'rb') as f:
    image_bytes = f.read()

res = ocr.classification(image_bytes)
print(res)
