import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import numpy as np
import os

# --------------------------------
# 1. Improved Neural Codec (AutoEncoder)
# --------------------------------
class AutoEncoder(nn.Module):
    def __init__(self):
        super(AutoEncoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=2, padding=1),  
            nn.BatchNorm2d(16),  
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1),  
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),  
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),  
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, 4, stride=2, padding=1),  
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 3, 4, stride=2, padding=1),   
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded


def train_autoencoder(model, image_tensor, epochs=100, lr=0.001):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    model.train()
    print("Training autoencoder...")
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        encoded, decoded = model(image_tensor)
        loss = criterion(decoded, image_tensor)
        
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.6f}")
    
    model.eval()
    return model


def load_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)  # [1, 3, 128, 128]
    return image_tensor, image

def save_compressed(tensor, path='compressed.pt'):
    torch.save(tensor, path)

def load_compressed(path='compressed.pt'):
    return torch.load(path)

def save_model(model, path='autoencoder_model.pt'):
    torch.save(model.state_dict(), path)

def load_model(model, path='autoencoder_model.pt'):
    model.load_state_dict(torch.load(path))
    return model


def calculate_mse(original, reconstructed):
    return torch.mean((original - reconstructed) ** 2).item()

def calculate_ssim(original_tensor, reconstructed_tensor):
    original = original_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    recon = reconstructed_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    
    return ssim(original, recon, channel_axis=2, data_range=1.0)

def calculate_compression_ratio(original_size, compressed_size):
    return original_size / compressed_size


def show_images(original_img, reconstructed_tensor, mse_val, ssim_val):
    reconstructed_img = reconstructed_tensor.squeeze(0).permute(1, 2, 0).detach().numpy()

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].imshow(original_img)
    axs[0].set_title("Original Image")
    axs[0].axis('off')

    axs[1].imshow(reconstructed_img)
    axs[1].set_title(f"Reconstructed Image\nMSE: {mse_val:.4f}, SSIM: {ssim_val:.4f}")
    axs[1].axis('off')

    plt.suptitle("Neural Codec Results", fontsize=16)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    image_path = "image/image1.jpg"      # Change to your image path
    compressed_file = "compressed.pt"
    model_file = "autoencoder_model.pt"

   
    image_tensor, original_image = load_image(image_path)
    
  
    model = AutoEncoder()
    
 
    if os.path.exists(model_file):
        print("Loading pre-trained model...")
        model = load_model(model, model_file)
        model.eval()
    else:
        print("No pre-trained model found. Training new model...")
        model = train_autoencoder(model, image_tensor, epochs=200)
        save_model(model, model_file)
        print(f"Model saved to {model_file}")

    # Encode → Save → Load → Decode
    with torch.no_grad():
        encoded, _ = model(image_tensor)
        save_compressed(encoded, compressed_file)
        encoded_loaded = load_compressed(compressed_file)
        reconstructed = model.decoder(encoded_loaded)

    original_size = image_tensor.numel() * 4  # 4 bytes per float32
    compressed_size = encoded.numel() * 4
    compression_ratio = calculate_compression_ratio(original_size, compressed_size)

    # Evaluate
    mse_value = calculate_mse(image_tensor, reconstructed)
    ssim_value = calculate_ssim(image_tensor, reconstructed)

    print(f"\n{'='*50}")
    print(f"NEURAL CODEC RESULTS")
    print(f"{'='*50}")
    print(f"Original size      : {original_size:,} bytes")
    print(f"Compressed size    : {compressed_size:,} bytes")
    print(f"Compression ratio  : {compression_ratio:.2f}:1")
    print(f"MSE Error          : {mse_value:.6f}")
    print(f"SSIM Score         : {ssim_value:.6f}")
    print(f"{'='*50}")

    # Show results
    show_images(original_image, reconstructed, mse_value, ssim_value)