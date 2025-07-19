import pywt
import numpy as np
from PIL import Image

def dwt_compress(input_path, output_path, quality=85, wavelet='haar', level=3):
    img = Image.open(input_path).convert('L')
    img_array = np.array(img, dtype=np.float32) / 255.0
    

    coeffs = pywt.wavedec2(img_array, wavelet, level=level)

    threshold = (100 - quality) / 100.0
    coeffs_thresh = [coeffs[0]]
    for i in range(1, len(coeffs)):
        coeffs_thresh.append(tuple(
            pywt.threshold(c, threshold, mode='soft') for c in coeffs[i]
        ))
    
    
    reconstructed = pywt.waverec2(coeffs_thresh, wavelet)
    reconstructed = np.clip(reconstructed, 0, 1)
    
    
    compressed_img = (reconstructed * 255).astype(np.uint8)
    Image.fromarray(compressed_img).save(output_path)