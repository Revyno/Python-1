import heapq
from collections import defaultdict, Counter
import re

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

class TextCompression:
    def __init__(self):
        pass
    
    def huffman_compress(self, text):
        """Huffman Coding - Lossless Compression"""
        if not text:
            return b'', {}
        
        # Count frequency of each character
        freq = Counter(text)
        
        # Build Huffman tree
        heap = [Node(char, freq) for char, freq in freq.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            merged = Node(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            
            heapq.heappush(heap, merged)
        
        root = heap[0]
        
        # Generate codes
        codes = {}
        def generate_codes(node, code=""):
            if node:
                if node.char is not None:
                    codes[node.char] = code if code else "0"
                generate_codes(node.left, code + "0")
                generate_codes(node.right, code + "1")
        
        generate_codes(root)
        
        # Encode text
        encoded_text = ''.join(codes[char] for char in text)
        
        # Convert to bytes
        # Pad to make it byte-aligned
        padding = 8 - len(encoded_text) % 8
        if padding != 8:
            encoded_text += '0' * padding
        
        # Convert binary string to bytes
        compressed_data = bytearray()
        for i in range(0, len(encoded_text), 8):
            byte = encoded_text[i:i+8]
            compressed_data.append(int(byte, 2))
        
        return bytes(compressed_data), codes
    
    def lz77_compress(self, text, window_size=20):
        """LZ77 Compression Algorithm - Lossless"""
        compressed = []
        i = 0
        
        while i < len(text):
            match_length = 0
            match_offset = 0
            
            # Search for matches in the sliding window
            start = max(0, i - window_size)
            for j in range(start, i):
                length = 0
                while (i + length < len(text) and 
                       j + length < i and 
                       text[j + length] == text[i + length]):
                    length += 1
                
                if length > match_length:
                    match_length = length
                    match_offset = i - j
            
            if match_length > 0:
                # Found a match
                next_char = text[i + match_length] if i + match_length < len(text) else ''
                compressed.append((match_offset, match_length, next_char))
                i += match_length + 1
            else:
                # No match found
                compressed.append((0, 0, text[i]))
                i += 1
        
        return compressed
    
    def rle_compress(self, text):
        """Run Length Encoding - Lossless"""
        if not text:
            return ""
        
        compressed = []
        i = 0
        
        while i < len(text):
            current_char = text[i]
            count = 1
            
            while i + count < len(text) and text[i + count] == current_char:
                count += 1
            
            if count > 1:
                compressed.append(f"{count}{current_char}")
            else:
                compressed.append(current_char)
            
            i += count
        
        return ''.join(compressed)