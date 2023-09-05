from PIL import Image
import numpy as np
import ddddocr

def get_slider_offset(captcha_img):
    # Load the captcha image
    img = Image.open(captcha_img)
    
    # Split the image into left and right halves
    width, height = img.size
    left = img.crop((0, 0, width//2, height))
    right = img.crop((width//2, 0, width//2 + width//2, height))
    
    # Convert to numpy arrays
    left_arr = np.array(left)
    right_arr = np.array(right)
    
    # Calculate the difference between the two halves 
    # to find the offset of the slider
    diff = np.abs(left_arr - right_arr)
    offset = np.sum(diff, axis=(0,1))
    
    # The peak in the difference indicates the vertical 
    # offset of the slider
    slider_offset = np.argmax(offset)
    
    return slider_offset

def getSlidingCoords(img_target, img_background):
    det = ddddocr.DdddOcr(det=False, ocr=False)
  
    with open(img_target, 'rb') as f:
        target_bytes = f.read()
    
    with open(img_background, 'rb') as f:
        background_bytes = f.read()
    
    res = det.slide_match(target_bytes, background_bytes)
    
    print(res)

# Example usage
img_target = r"C:\Users\Admin\Pictures\slide_auth_small.png"
img_background = r"C:\Users\Admin\Pictures\slide_auth.png"
res = getSlidingCoords(img_target, img_background)
# print(res)

# img_path = r"C:\Users\Admin\Pictures\slide_auth3.png"
# offset = get_slider_offset(img_path)
# print("Slider offset:", offset)