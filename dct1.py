
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pywt
# metode dct

def lossless_image_comparison(image1_path, image2_path):
    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')
    
   
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    
    matches = np.sum(arr1 == arr2)
    total = arr1.size
    
    similarity = matches / total
    return similarity
# metode dct

def dct_image_comparison(image1_path, image2_path, block_size=8):
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    
    # Resize image2 agar sama ukuran dengan image1 jika diperlukan
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    #  DCT 
    def compute_dct(image):
        h, w = image.shape
        dct_blocks = np.zeros((h, w))
        for i in range(0, h, block_size):
            for j in range(0, w, block_size):
                block = image[i:i+block_size, j:j+block_size]
                if block.shape[0] == block_size and block.shape[1] == block_size:
                    dct_blocks[i:i+block_size, j:j+block_size] = cv2.dct(block.astype(np.float32))
        return dct_blocks
    
    dct1 = compute_dct(img1)
    dct2 = compute_dct(img2)
    
    # MDCT
    mse = np.mean((dct1 - dct2) ** 2)
    if mse == 0:
        return 1.0
    max_pixel = 255.0
    similarity = 1 - (mse / (max_pixel ** 2))
    return similarity

#  DWT
def dwt_image_comparison(image1_path, image2_path, wavelet='haar', level=1):
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    
    # Resize image2 agar sama ukuran dengan image1 jika diperlukan
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Menghitung DWT
    def compute_dwt(image):
        coeffs = pywt.wavedec2(image, wavelet, level=level)
        return coeffs
    
    coeffs1 = compute_dwt(img1)
    coeffs2 = compute_dwt(img2)
    
    #  DWT
    similarity = 0
    count = 0
    

    cA1 = coeffs1[0]
    cA2 = coeffs2[0]
    mse = np.mean((cA1 - cA2) ** 2)
    max_pixel = np.maximum(np.max(cA1), np.max(cA2))
    if max_pixel > 0:
        similarity += 1 - (mse / (max_pixel ** 2))
        count += 1
    
    # Band detail
    for i in range(1, len(coeffs1)):
        (cH1, cV1, cD1) = coeffs1[i]
        (cH2, cV2, cD2) = coeffs2[i]
        
        for band1, band2 in [(cH1, cH2), (cV1, cV2), (cD1, cD2)]:
            mse = np.mean((band1 - band2) ** 2)
            max_pixel = np.maximum(np.max(band1), np.max(band2))
            if max_pixel > 0:
                similarity += 1 - (mse / (max_pixel ** 2))
                count += 1
    
    if count > 0:
        return similarity / count
    return 0.0


def tampilkan_gambar(image1_path, image2_path, similarity_scores):
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img1)
    axes[0].set_title("Gambar 1")
    axes[0].axis('off')
    
    axes[1].imshow(img2)
    axes[1].set_title("Gambar 2")
    axes[1].axis('off')
    
    title = (
        f"Similarity Scores:\n"
        f"Pixel-by-Pixel: {similarity_scores['pixel']:.4f}\n"
        f"DCT: {similarity_scores['dct']:.4f}\n"
        f"DWT: {similarity_scores['dwt']:.4f}"
    )
    
    plt.suptitle(title, fontsize=12)
    plt.show()


if __name__ == "__main__":
    image1 = "image/image1.jpg"   
    image2 = "image/image2.jpg"   
    
  
    sim_scores = {
        'pixel': lossless_image_comparison(image1, image2),
        'dct': dct_image_comparison(image1, image2),
        'dwt': dwt_image_comparison(image1, image2)
    }
    
    print("Similarity Scores:")
    print(f"Pixel-by-Pixel: {sim_scores['pixel']:.4f}")
    print(f"DCT: {sim_scores['dct']:.4f}")
    print(f"DWT: {sim_scores['dwt']:.4f}")
    
    
    tampilkan_gambar(image1, image2, sim_scores)