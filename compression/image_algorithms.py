from PIL import Image, ImageOps
import os

class ImageCompression:
    def __init__(self):
        pass
    
    def jpeg_compress(self, input_path, quality=85):
        """JPEG Compression - Lossy"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Generate output filename
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_compressed_q{quality}.jpg"
                
                # Save with specified quality
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                return output_path
        except Exception as e:
            raise Exception(f"JPEG compression failed: {str(e)}")
    
    def png_compress(self, input_path):
        """PNG Compression - Lossless"""
        try:
            with Image.open(input_path) as img:
                # Generate output filename
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_compressed.png"
                
                # Save with PNG compression
                img.save(output_path, 'PNG', optimize=True)
                
                return output_path
        except Exception as e:
            raise Exception(f"PNG compression failed: {str(e)}")
    
    def webp_compress(self, input_path, quality=85):
        """WebP Compression - Lossy/Lossless"""
        try:
            with Image.open(input_path) as img:
                # Generate output filename
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_compressed.webp"
                
                # Save as WebP
                img.save(output_path, 'WEBP', quality=quality, optimize=True)
                
                return output_path
        except Exception as e:
            raise Exception(f"WebP compression failed: {str(e)}")