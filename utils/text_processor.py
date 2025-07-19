import re
import string

class TextProcessor:
    def __init__(self):
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
    
    def preprocess(self, text):
        """Preprocess text for better compression"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove unnecessary punctuation for compression
        text = text.strip()
        
        return text
    
    def postprocess(self, text):
        """Postprocess decompressed text"""
        # Add proper spacing and formatting
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def calculate_metrics(self, original, compressed):
        """Calculate compression metrics"""
        original_size = len(original.encode('utf-8'))
        compressed_size = len(str(compressed).encode('utf-8'))
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': (1 - compressed_size / original_size) * 100,
            'space_saved': original_size - compressed_size
        }