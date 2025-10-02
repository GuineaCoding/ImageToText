from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import os
import sys
import subprocess

app = Flask(__name__)

# Try to import pytesseract
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
        '/app/.apt/usr/bin/tesseract',
        '/usr/bin/tesseract'  # Render path
    ]
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found tesseract at: {path}")
            return path
    print("Tesseract not found in any standard paths")
    return None

def setup_tesseract():
    """Setup tesseract path and verify it works"""
    if not TESSERACT_AVAILABLE:
        return False
        
    tesseract_path = find_tesseract()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        try:
            # Test if tesseract works
            result = subprocess.run([tesseract_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"Tesseract is working: {result.stdout.strip()}")
                return True
            else:
                print(f"Tesseract test failed: {result.stderr}")
        except Exception as e:
            print(f"Tesseract test error: {e}")
    
    return False

# Setup tesseract on app start
TESSERACT_WORKING = setup_tesseract()

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
    
    # Check if Tesseract is available and working
    if not TESSERACT_AVAILABLE:
        return jsonify({'error': 'OCR engine not available. pytesseract not installed.'}), 500
    
    if not TESSERACT_WORKING:
        return jsonify({'error': 'Tesseract OCR is installed but not working properly. Please check server logs.'}), 500
    
    try:
        # Open image
        img = Image.open(io.BytesIO(file.read()))
        
        # Convert image to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Perform OCR with configuration
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:,.<>?/~` '  
        text = pytesseract.image_to_string(img, config=custom_config)
        
        return jsonify({'text': text.strip()})
    
    except Exception as e:
        app.logger.error(f"OCR Error: {str(e)}")
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy' if TESSERACT_WORKING else 'unhealthy',
        'tesseract_available': TESSERACT_AVAILABLE,
        'tesseract_working': TESSERACT_WORKING,
        'tesseract_path': find_tesseract() if TESSERACT_AVAILABLE else None
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)