from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import time
from compression.text_algorithms import TextCompression
from compression.image_algorithms import ImageCompression
from utils.helpers import allowed_file, get_file_size, format_compression_ratio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-compression')
def text_compression():
    return render_template('text_compression.html')

@app.route('/image-compression')
def image_compression():
    return render_template('image_compression.html')

@app.route('/api/compress-text', methods=['POST'])
def compress_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        algorithm = data.get('algorithm', 'huffman')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        text_compressor = TextCompression()
        start_time = time.time()
        
        if algorithm == 'huffman':
            compressed_data, tree = text_compressor.huffman_compress(text)
            compression_time = time.time() - start_time
            
            original_size = len(text.encode('utf-8'))
            compressed_size = len(compressed_data)
            ratio = format_compression_ratio(original_size, compressed_size)
            
            return jsonify({
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': ratio,
                'compression_time': round(compression_time, 4),
                'algorithm': 'Huffman Coding (Lossless)',
                'compressed_data': compressed_data.hex() if isinstance(compressed_data, bytes) else str(compressed_data)
            })
            
        elif algorithm == 'lz77':
            compressed_data = text_compressor.lz77_compress(text)
            compression_time = time.time() - start_time
            
            original_size = len(text.encode('utf-8'))
            compressed_size = len(str(compressed_data).encode('utf-8'))
            ratio = format_compression_ratio(original_size, compressed_size)
            
            return jsonify({
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': ratio,
                'compression_time': round(compression_time, 4),
                'algorithm': 'LZ77 (Lossless)',
                'compressed_data': str(compressed_data)
            })
            
        elif algorithm == 'rle':
            compressed_data = text_compressor.rle_compress(text)
            compression_time = time.time() - start_time
            
            original_size = len(text.encode('utf-8'))
            compressed_size = len(compressed_data.encode('utf-8'))
            ratio = format_compression_ratio(original_size, compressed_size)
            
            return jsonify({
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': ratio,
                'compression_time': round(compression_time, 4),
                'algorithm': 'Run Length Encoding (Lossless)',
                'compressed_data': compressed_data
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compress-image', methods=['POST'])
def compress_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        algorithm = request.form.get('algorithm', 'jpeg')
        quality = int(request.form.get('quality', 85))
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename, ['png', 'jpg', 'jpeg', 'bmp', 'tiff']):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image_compressor = ImageCompression()
            start_time = time.time()
            
            if algorithm == 'jpeg':
                compressed_path = image_compressor.jpeg_compress(filepath, quality)
                compression_time = time.time() - start_time
                
                original_size = get_file_size(filepath)
                compressed_size = get_file_size(compressed_path)
                ratio = format_compression_ratio(original_size, compressed_size)
                
                # Extract just the filename from the path for download
                compressed_filename = os.path.basename(compressed_path)
                original_filename = os.path.basename(filepath)
                
                return jsonify({
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': ratio,
                    'compression_time': round(compression_time, 4),
                    'algorithm': f'JPEG (Lossy, Quality: {quality})',
                    'original_filename': original_filename,
                    'compressed_filename': compressed_filename,
                    'original_path': f'/static/uploads/{original_filename}',
                    'compressed_path': f'/static/uploads/{compressed_filename}'
                })
                
            elif algorithm == 'png':
                compressed_path = image_compressor.png_compress(filepath)
                compression_time = time.time() - start_time
                
                original_size = get_file_size(filepath)
                compressed_size = get_file_size(compressed_path)
                ratio = format_compression_ratio(original_size, compressed_size)
                
                # Extract just the filename from the path for download
                compressed_filename = os.path.basename(compressed_path)
                original_filename = os.path.basename(filepath)
                
                return jsonify({
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': ratio,
                    'compression_time': round(compression_time, 4),
                    'algorithm': 'PNG (Lossless)',
                    'original_filename': original_filename,
                    'compressed_filename': compressed_filename,
                    'original_path': f'/static/uploads/{original_filename}',
                    'compressed_path': f'/static/uploads/{compressed_filename}'
                })
                
            elif algorithm == 'webp':
                compressed_path = image_compressor.webp_compress(filepath, quality)
                compression_time = time.time() - start_time
                
                original_size = get_file_size(filepath)
                compressed_size = get_file_size(compressed_path)
                ratio = format_compression_ratio(original_size, compressed_size)
                
                # Extract just the filename from the path for download
                compressed_filename = os.path.basename(compressed_path)
                original_filename = os.path.basename(filepath)
                
                return jsonify({
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': ratio,
                    'compression_time': round(compression_time, 4),
                    'algorithm': f'WebP (Quality: {quality})',
                    'original_filename': original_filename,
                    'compressed_filename': compressed_filename,
                    'original_path': f'/static/uploads/{original_filename}',
                    'compressed_path': f'/static/uploads/{compressed_filename}'
                })
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # Sanitize filename to prevent directory traversal
        secure_name = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get the original filename without timestamp prefix if exists
        display_name = secure_name
        if '_compressed' in secure_name:
            # Keep the compressed suffix in the download name
            display_name = secure_name
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=display_name,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# Add a route to serve uploaded files for preview
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    try:
        secure_name = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)