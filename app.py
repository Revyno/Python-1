from flask import Flask, request, jsonify, render_template, send_file
import os
import torch
import json
from werkzeug.utils import secure_filename
from utils.neural_codec import NeuralCodec
from utils.text_processor import TextProcessor
import tempfile
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize neural codec
neural_codec = NeuralCodec()
text_processor = TextProcessor()

ALLOWED_EXTENSIONS = {'txt', 'json', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_text():
    try:
        # Get compression parameters
        compression_level = float(request.form.get('compression_level', 0.5))
        quality = float(request.form.get('quality', 0.8))
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                os.remove(filepath)
        else:
            text = request.form.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Preprocess text
        processed_text = text_processor.preprocess(text)
        
        # Apply neural codec compression
        compressed_data = neural_codec.compress(
            processed_text, 
            compression_level=compression_level,
            quality=quality
        )
        
        # Calculate compression ratio
        original_size = len(text.encode('utf-8'))
        compressed_size = len(compressed_data['encoded'])
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return jsonify({
            'success': True,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': f"{compression_ratio:.2f}%",
            'compressed_data': compressed_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decompress', methods=['POST'])
def decompress_text():
    try:
        compressed_data = request.get_json()
        
        if not compressed_data:
            return jsonify({'error': 'No compressed data provided'}), 400
        
        # Decompress using neural codec
        decompressed_text = neural_codec.decompress(compressed_data)
        
        return jsonify({
            'success': True,
            'decompressed_text': decompressed_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<format>')
def download_file(format):
    try:
        # Get data from session or temporary storage
        data = request.args.get('data')
        filename = request.args.get('filename', 'compressed_data')
        
        if not data:
            return jsonify({'error': 'No data to download'}), 400
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format}') as tmp:
            if format == 'json':
                json.dump(json.loads(data), tmp, indent=2)
            else:
                tmp.write(data)
            tmp_path = tmp.name
        
        return send_file(tmp_path, as_attachment=True, download_name=f'{filename}.{format}')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)