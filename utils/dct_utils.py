import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def dct_compress(input_path, output_path, quality=85):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read image")
    
    img = img.astype(np.float32) / 255.0
    
   
    h, w = img.shape
    pad_h = (8 - h % 8) % 8
    pad_w = (8 - w % 8) % 8
    
    if pad_h > 0 or pad_w > 0:
        img = np.pad(img, ((0, pad_h), (0, pad_w)), mode='constant')
    

    compressed = np.zeros_like(img)
    for i in range(0, img.shape[0], 8):
        for j in range(0, img.shape[1], 8):
            block = img[i:i+8, j:j+8]
            dct_block = cv2.dct(block)
            
       
            threshold = (100 - quality) / 100.0 * np.max(np.abs(dct_block))
            dct_block[np.abs(dct_block) < threshold] = 0
            
            compressed[i:i+8, j:j+8] = cv2.idct(dct_block)
    

    compressed = np.clip(compressed, 0, 1)
    compressed_img = (compressed * 255).astype(np.uint8)
    Image.fromarray(compressed_img).save(output_path)