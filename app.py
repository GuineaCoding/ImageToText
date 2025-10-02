# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import os
import sys

app = Flask(__name__)


try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def find_tesseract():
    """Find tesseract executable path"""
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract', 
        '/app/.apt/usr/bin/tesseract'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if Tesseract is available
    if not TESSERACT_AVAILABLE:
        return jsonify({'error': 'OCR engine not available. Please check server configuration.'}), 500
    
    try:
        # Try to set tesseract path for Render
        tesseract_path = find_tesseract()
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Open image
        img = Image.open(io.BytesIO(file.read()))
        
        # Perform OCR with configuration
        custom_config = r'--oem 3 --psm 6'  
        text = pytesseract.image_to_string(img, config=custom_config)
        
        return jsonify({'text': text.strip()})
    
    except Exception as e:
        app.logger.error(f"OCR Error: {str(e)}")
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'tesseract_available': TESSERACT_AVAILABLE,
        'tesseract_path': find_tesseract() if TESSERACT_AVAILABLE else None
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)