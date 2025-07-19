import torch
import torch.nn as nn
import numpy as np
import base64
import json
from typing import Tuple, Dict, Any

# --- Enhanced Neural Codec Model with Lossy Compression ---
class LossyTextAutoencoder(nn.Module):
    def __init__(self, vocab_size, hidden_dim=32, compression_ratio=4):
        super(LossyTextAutoencoder, self).__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.bottleneck_dim = max(1, hidden_dim // compression_ratio)  # Lossy bottleneck
        
        # Encoder with progressive dimensionality reduction
        self.encoder = nn.Sequential(
            nn.Linear(vocab_size, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),  # Add noise for lossy compression
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, self.bottleneck_dim),  # Bottleneck layer
            nn.Tanh()  # Bounded activation for better compression
        )
        
        # Decoder with progressive dimensionality expansion
        self.decoder = nn.Sequential(
            nn.Linear(self.bottleneck_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, vocab_size),
            nn.Softmax(dim=-1)  # Probabilistic output
        )
        
        # Quantization parameters for lossy compression
        self.quantization_levels = 256  # 8-bit quantization
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded, encoded
    
    def quantize_latent(self, latent, quality_factor=0.8):
        """Apply quantization for lossy compression"""
        # Scale quality factor (0.1 = high compression/low quality, 1.0 = low compression/high quality)
        levels = max(8, int(self.quantization_levels * quality_factor))
        
        # Quantize to reduced precision
        min_val = latent.min()
        max_val = latent.max()
        
        # Normalize to [0, levels-1]
        normalized = (latent - min_val) / (max_val - min_val + 1e-8)
        quantized = torch.round(normalized * (levels - 1))
        
        # Convert back to original range
        dequantized = (quantized / (levels - 1)) * (max_val - min_val) + min_val
        
        return dequantized, {'min_val': min_val.item(), 'max_val': max_val.item(), 'levels': levels}

# --- Helper Functions ---
def text_to_tensor(text, vocab):
    """Convert text to one-hot tensor representation"""
    tensor = torch.zeros(len(text), len(vocab))
    for i, char in enumerate(text):
        if char in vocab:
            tensor[i][vocab.index(char)] = 1
    return tensor

def tensor_to_text(tensor, vocab, threshold=0.5):
    """Convert tensor back to text with confidence threshold"""
    text = ''
    for vec in tensor:
        # Get the character with highest probability
        max_idx = torch.argmax(vec).item()
        max_prob = vec[max_idx].item()
        
        # Only use character if confidence is above threshold
        if max_prob > threshold:
            text += vocab[max_idx]
        else:
            # Use most likely character but mark uncertainty
            text += vocab[max_idx]  # Could add uncertainty markers here
    return text

# --- Lossy Compression Functions ---
def compress_neural_lossy(text, model, vocab, quality_factor=0.8):
    """Compress text using lossy neural codec"""
    tensor = text_to_tensor(text, vocab)
    
    with torch.no_grad():
        _, encoded = model(tensor)
        
        # Apply lossy quantization
        quantized_encoded, quant_info = model.quantize_latent(encoded, quality_factor)
    
    # Convert to bytes with quantization info
    encoded_bytes = quantized_encoded.numpy().astype(np.float32).tobytes()
    
    # Create compressed data structure
    compressed_data = {
        'encoded': base64.b64encode(encoded_bytes).decode('utf-8'),
        'quant_info': quant_info,
        'vocab': vocab,
        'shape': quantized_encoded.shape,
        'quality': quality_factor
    }
    
    return json.dumps(compressed_data)

def decompress_neural_lossy(compressed_json, model):
    """Decompress text from lossy neural codec"""
    try:
        compressed_data = json.loads(compressed_json)
        
        # Extract components
        encoded_b64 = compressed_data['encoded']
        quant_info = compressed_data['quant_info']
        vocab = compressed_data['vocab']
        shape = compressed_data['shape']
        
        # Decode from base64
        encoded_bytes = base64.b64decode(encoded_b64)
        encoded_array = np.frombuffer(encoded_bytes, dtype=np.float32)
        encoded_tensor = torch.tensor(encoded_array, dtype=torch.float32).reshape(shape)
        
        # Decode through neural network
        with torch.no_grad():
            decoded = model.decoder(encoded_tensor)
        
        return tensor_to_text(decoded, vocab)
    
    except Exception as e:
        return f"Decompression error: {str(e)}"

# --- Evaluation Functions ---
def calculate_compression_metrics(original_text, compressed_data, decompressed_text):
    """Calculate compression ratio and quality metrics"""
    original_size = len(original_text.encode('utf-8'))
    compressed_size = len(compressed_data.encode('utf-8'))
    
    compression_ratio = original_size / compressed_size
    
    # Character-level accuracy
    char_accuracy = sum(1 for a, b in zip(original_text, decompressed_text) if a == b) / len(original_text)
    
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'character_accuracy': char_accuracy,
        'space_savings': (1 - compressed_size / original_size) * 100
    }

def train_model_on_text(model, text, vocab, epochs=300, lr=0.01):
    """Train the model on the input text"""
    data = text_to_tensor(text, vocab)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    
    print(f"Training model on {len(text)} characters...")
    
    for epoch in range(epochs):
        output, _ = model(data)
        loss = loss_fn(output, data)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 50 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f}")
    
    return model

# --- Main Program ---
def main():
    print("=== Lossy Neural Codec for Text Compression ===\n")
    
    # Get input
    text = input("Enter text to compress: ").strip()
    
    if not text:
        print("Text cannot be empty.")
        return
    
    # Get quality setting
    print("\nQuality Settings:")
    print("1. High Quality (0.9) - Better reconstruction, larger file")
    print("2. Medium Quality (0.7) - Balanced")
    print("3. Low Quality (0.5) - Smaller file, some quality loss")
    print("4. Very Low Quality (0.3) - Maximum compression")
    
    quality_choice = input("Choose quality (1-4) or enter custom value (0.1-1.0): ").strip()
    
    quality_map = {'1': 0.9, '2': 0.7, '3': 0.5, '4': 0.3}
    
    if quality_choice in quality_map:
        quality_factor = quality_map[quality_choice]
    else:
        try:
            quality_factor = float(quality_choice)
            quality_factor = max(0.1, min(1.0, quality_factor))
        except ValueError:
            quality_factor = 0.7
            print("Invalid input, using medium quality (0.7)")
    
    print(f"\nUsing quality factor: {quality_factor}")
    
    # Create vocabulary and model
    vocab = sorted(set(text))
    print(f"Vocabulary size: {len(vocab)} unique characters")
    
    # Create model with compression ratio based on quality
    compression_ratio = int(8 * (1.1 - quality_factor))  # Higher quality = lower compression ratio
    model = LossyTextAutoencoder(vocab_size=len(vocab), hidden_dim=64, compression_ratio=compression_ratio)
    
    # Train model
    print(f"\nTraining neural codec (compression ratio: {compression_ratio}:1)...")
    model = train_model_on_text(model, text, vocab)
    
    # Compress
    print("\nCompressing...")
    compressed_data = compress_neural_lossy(text, model, vocab, quality_factor)
    
    # Decompress
    print("Decompressing...")
    decompressed_text = decompress_neural_lossy(compressed_data, model)
    
    # Calculate metrics
    metrics = calculate_compression_metrics(text, compressed_data, decompressed_text)
    
    # Display results
    print("\n" + "="*60)
    print("COMPRESSION RESULTS")
    print("="*60)
    print(f"Original text: {text}")
    print(f"Decompressed:  {decompressed_text}")
    print(f"\nOriginal size:     {metrics['original_size']:,} bytes")
    print(f"Compressed size:   {metrics['compressed_size']:,} bytes")
    print(f"Compression ratio: {metrics['compression_ratio']:.2f}:1")
    print(f"Space savings:     {metrics['space_savings']:.1f}%")
    print(f"Character accuracy: {metrics['character_accuracy']*100:.1f}%")
    print(f"Quality factor:    {quality_factor}")
    print("="*60)
    
    # Show compressed data (truncated)
    print(f"\nCompressed data (first 100 chars): {compressed_data[:100]}...")
    
    if metrics['character_accuracy'] < 0.9:
        print(f"\n⚠️  Warning: Character accuracy is {metrics['character_accuracy']*100:.1f}% - some information was lost during compression!")
    else:
        print(f"\n✅ Good compression with {metrics['character_accuracy']*100:.1f}% accuracy!")

if __name__ == '__main__':
    main()