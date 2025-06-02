from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Fungsi menghitung similarity (pixel-by-pixel)
def lossless_image_comparison(image1_path, image2_path):
    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')
    
    # Resize image2 agar sama ukuran dengan image1 jika diperlukan
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
    
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    # Hitung jumlah pixel yang sama
    matches = np.sum(arr1 == arr2)
    total = arr1.size
    
    similarity = matches / total
    return similarity

# Fungsi menampilkan gambar berdampingan
def tampilkan_gambar(image1_path, image2_path, similarity_score):
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img1)
    axes[0].set_title("Gambar 1")
    axes[0].axis('off')
    
    axes[1].imshow(img2)
    axes[1].set_title("Gambar 2")
    axes[1].axis('off')
    
    plt.suptitle(f"Lossless Pixel Similarity: {similarity_score:.4f}", fontsize=16)
    plt.show()

# ======== Main Program ========
if __name__ == "__main__":
    image1 = "image/image1.jpg"   # Ganti dengan path gambar 1
    image2 = "image/image2.jpg"   # Ganti dengan path gambar 2
    
    sim_score = lossless_image_comparison(image1, image2)
    print(f"Lossless Pixel Similarity: {sim_score:.4f}")
    
    # Tampilkan gambar dengan skor similarity
    tampilkan_gambar(image1, image2, sim_score)
