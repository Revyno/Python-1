import tensorflow as tf
import numpy as np
from PIL import Image

def build_autoencoder():
    input_img = tf.keras.layers.Input(shape=(256, 256, 1))
    
    # Encoder
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(x)
    encoded = tf.keras.layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Decoder
    x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(encoded)
    x = tf.keras.layers.UpSampling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.UpSampling2D((2, 2))(x)
    decoded = tf.keras.layers.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
    
    autoencoder = tf.keras.models.Model(input_img, decoded)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
    return autoencoder

# Global model instance
autoencoder = None

def dnn_compress(input_path, output_path, quality=85):
    global autoencoder
    if autoencoder is None:
        autoencoder = build_autoencoder()
        # Load weights if available
    
    img = Image.open(input_path).convert('L')
    img = img.resize((256, 256))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=-1)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Adjust compression strength based on quality
    compressed = autoencoder.predict(img_array)
    compressed = np.clip(compressed * (quality / 100.0), 0, 1)
    
    # Save result
    compressed_img = (compressed[0,:,:,0] * 255).astype(np.uint8)
    Image.fromarray(compressed_img).save(output_path)