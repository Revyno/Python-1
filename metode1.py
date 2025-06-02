import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt

# Fungsi ekstraksi fitur dari gambar menggunakan ResNet50
def extract_features(image_path, model, transform):
    img = Image.open(image_path).convert('RGB')
    img_t = transform(img).unsqueeze(0)
    with torch.no_grad():
        features = model(img_t)
    return features.numpy().flatten()

# Fungsi menghitung similarity (deep learning cosine similarity)
def deep_image_comparison(image1_path, image2_path):
    # Load pretrained ResNet50
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.fc = torch.nn.Identity()  # Hapus layer klasifikasi terakhir
    model.eval()

    # Preprocessing
    transform = weights.transforms()

    # Ekstrak fitur
    feat1 = extract_features(image1_path, model, transform)
    feat2 = extract_features(image2_path, model, transform)

    # Hitung cosine similarity
    similarity = cosine_similarity([feat1], [feat2])[0][0]
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
    
    plt.suptitle(f"Similarity Score (Cosine): {similarity_score:.4f}", fontsize=16)
    plt.show()

# ======== Main Program ========
if __name__ == "__main__":
    image1 = "image/image1.jpg"   # Ganti dengan path gambar 1
    image2 = "image/image2.jpg"   # Ganti dengan path gambar 2
    
    sim_score = deep_image_comparison(image1, image2)
    print(f"Deep Learning Cosine Similarity: {sim_score:.4f}")
    
    # Tampilkan gambar dengan skor similarity
    tampilkan_gambar(image1, image2, sim_score)
