import os

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)

def format_compression_ratio(original_size, compressed_size):
    """Calculate and format compression ratio"""
    if original_size == 0:
        return "0%"
    
    ratio = (1 - compressed_size / original_size) * 100
    return f"{ratio:.2f}%"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"
