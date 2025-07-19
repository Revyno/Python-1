import os

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(basedir, 'temp')
COMPRESSED_FOLDER = os.path.join(basedir, 'static', 'compressed')
DOCUMENT_FOLDER = os.path.join(basedir, 'static', 'documents')  # Add this line
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# Maximum upload size (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Secret key for session management
SECRET_KEY = 'your-secret-key-here'