import pywt
import numpy as np
from PIL import Image
import cv2
import tensorflow as tf
import heapq
from collections import defaultdict
import os
import time

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0

def format_compression_ratio(original_size, compressed_size):
    """Format compression ratio as percentage"""
    if original_size == 0:
        return "0%"
    
    ratio = (compressed_size / original_size) * 100
    return f"{ratio:.1f}%"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"
# metode hufman coding
class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_table(text):
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1
    return frequency

def build_huffman_tree(frequency):
    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char=char, freq=freq))
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heapq.heappop(heap)

def build_codes(root, current_code="", codes={}):
    if root is None:
        return
    
    if root.char is not None:
        codes[root.char] = current_code or "0"  # Handle single character case
        return
    
    build_codes(root.left, current_code + "0", codes)
    build_codes(root.right, current_code + "1", codes)
    
    return codes

def encode_text(text, codes):
    encoded_text = ""
    for char in text:
        encoded_text += codes[char]
    return encoded_text

def pad_encoded_text(encoded_text):
    extra_padding = 8 - len(encoded_text) % 8
    for i in range(extra_padding):
        encoded_text += "0"
    
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text
    return encoded_text

def get_byte_array(padded_encoded_text):
    if len(padded_encoded_text) % 8 != 0:
        raise ValueError("Encoded text not padded properly")
    
    b = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte, 2))
    return b

def huffman_compress(text):
    if not text:
        return {'compressed': '', 'codes': {}}
    
    frequency = build_frequency_table(text)
    root = build_huffman_tree(frequency)
    codes = build_codes(root)
    
    encoded_text = encode_text(text, codes)
    padded_encoded_text = pad_encoded_text(encoded_text)
    byte_array = get_byte_array(padded_encoded_text)
   
    compressed = ''.join([bin(byte)[2:].rjust(8, '0') for byte in byte_array])
    
    return {
        'compressed': compressed,
        'codes': codes
    }

def compress_text(text, algorithm='huffman'):
    """Compress text using the specified algorithm"""
    if algorithm.lower() != 'huffman':
        raise ValueError(f"Unsupported algorithm: {algorithm}. Only 'huffman' is currently supported.")
    
    start_time = time.time()
    result = huffman_compress(text)
    end_time = time.time()
    
    compressed_data = result['compressed']
    original_size = len(text.encode('utf-8'))
    compressed_size = len(compressed_data.encode('utf-8'))
    
    return {
        'compressed': compressed_data,
        'codes': result['codes'],
        'compression_time': round(end_time - start_time, 4),
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': format_compression_ratio(original_size, compressed_size)
    }

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

def build_autoencoder():
    input_img = tf.keras.layers.Input(shape=(256, 256, 1))
    
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(x)
    encoded = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    
    x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(encoded)
    x = tf.keras.layers.UpSampling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.UpSampling2D((2, 2))(x)
    decoded = tf.keras.layers.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
    
    autoencoder = tf.keras.models.Model(input_img, decoded)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
    return autoencoder

autoencoder = None

def dnn_compress(input_path, output_path, quality=85):
    global autoencoder
    if autoencoder is None:
        autoencoder = build_autoencoder()
    
    img = Image.open(input_path).convert('L')
    img = img.resize((256, 256))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=-1)
    img_array = np.expand_dims(img_array, axis=0)
    
    compressed = autoencoder.predict(img_array)
    compressed = np.clip(compressed * (quality / 100.0), 0, 1)
    
    compressed_img = (compressed[0,:,:,0] * 255).astype(np.uint8)
    Image.fromarray(compressed_img).save(output_path)

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

def compress_image(input_path, output_path, algorithm='jpeg', quality=85):
    """Compress image using the specified algorithm"""
    start_time = time.time()
    
    if algorithm.lower() == 'jpeg':
        dct_compress(input_path, output_path, quality)
    elif algorithm.lower() == 'png':
        img = Image.open(input_path)
        img.save(output_path, optimize=True, quality=quality)
    elif algorithm.lower() == 'webp':
        img = Image.open(input_path)
        img.save(output_path, format='WEBP', quality=quality)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    end_time = time.time()
    
    original_size = get_file_size(input_path)
    compressed_size = get_file_size(output_path)
    
    return {
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': format_compression_ratio(original_size, compressed_size),
        'compression_time': round(end_time - start_time, 4)
    }