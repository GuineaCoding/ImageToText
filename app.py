from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import os
import sys
import subprocess
import shutil

app = Flask(__name__)

# Try to import pytesseract
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✓ pytesseract imported successfully")
except ImportError as e:
    TESSERACT_AVAILABLE = False
    print(f"✗ pytesseract import failed: {e}")

def diagnose_tesseract():
    """Comprehensive tesseract diagnosis"""
    diagnostics = {
        'pytesseract_available': TESSERACT_AVAILABLE,
        'tesseract_found': False,
        'tesseract_version': None,
        'tesseract_path': None,
        'error': None
    }
    
    if not TESSERACT_AVAILABLE:
        diagnostics['error'] = 'pytesseract not available'
        return diagnostics
    
    # Method 1: Try to find tesseract using shutil.which
    tesseract_path = shutil.which('tesseract')
    if not tesseract_path:
        # Method 2: Check common paths
        common_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/app/.apt/usr/bin/tesseract',
            '/opt/homebrew/bin/tesseract'  # macOS
        ]
        for path in common_paths:
            if os.path.exists(path):
                tesseract_path = path
                break
    
    if not tesseract_path:
        diagnostics['error'] = 'Tesseract not found in PATH or common locations'
        return diagnostics
    
    diagnostics['tesseract_path'] = tesseract_path
    diagnostics['tesseract_found'] = True
    
    # Try to get version
    try:
        result = subprocess.run([tesseract_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            diagnostics['tesseract_version'] = result.stdout.strip()
            print(f"✓ Tesseract version: {result.stdout.strip()}")
        else:
            diagnostics['error'] = f"Version check failed: {result.stderr}"
    except Exception as e:
        diagnostics['error'] = f"Version check error: {str(e)}"
    
    return diagnostics

# Run diagnosis on startup
print("=== Tesseract Diagnosis ===")
diagnostics = diagnose_tesseract()
for key, value in diagnostics.items():
    print(f"{key}: {value}")

# Set tesseract path if found
if diagnostics['tesseract_found'] and not diagnostics.get('error'):
    pytesseract.pytesseract.tesseract_cmd = diagnostics['tesseract_path']
    TESSERACT_WORKING = True
    print("✓ Tesseract configured successfully")
else:
    TESSERACT_WORKING = False
    print("✗ Tesseract not working")

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
    
    if not TESSERACT_WORKING:
        return jsonify({
            'error': 'Tesseract OCR is not working properly',
            'diagnostics': diagnose_tesseract()
        }), 500
    
    try:
        # Open and validate image
        file_bytes = file.read()
        if not file_bytes:
            return jsonify({'error': 'Empty file'}), 400
            
        img = Image.open(io.BytesIO(file_bytes))
        
        # Convert image to supported format
        if img.mode in ('P', 'RGBA', 'LA'):
            img = img.convert('RGB')
        
        # Simple OCR without complex config first
        try:
            text = pytesseract.image_to_string(img)
        except Exception as ocr_error:
            # Try with basic config
            text = pytesseract.image_to_string(img, config='--psm 3')
        
        return jsonify({'text': text.strip() if text else ''})
    
    except Exception as e:
        app.logger.error(f"OCR Error: {str(e)}")
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Comprehensive health check"""
    diagnostics = diagnose_tesseract()
    status = 'healthy' if TESSERACT_WORKING else 'unhealthy'
    
    return jsonify({
        'status': status,
        'service': 'TextExtract Pro',
        'diagnostics': diagnostics
    })

@app.route('/test-ocr')
def test_ocr():
    """Test OCR with a simple built-in image"""
    if not TESSERACT_WORKING:
        return jsonify({'error': 'Tesseract not working', 'diagnostics': diagnose_tesseract()})
    
    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Create a test image
        img = Image.new('RGB', (400, 100), color='white')
        d = ImageDraw.Draw(img)
        
        # Try to use a basic font
        try:
            font = ImageFont.load_default()
            d.text((10, 10), "Hello World! Test 123", fill='black', font=font)
        except:
            # If font fails, just draw text without font
            d.text((10, 10), "Hello World! Test 123", fill='black')
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        
        return jsonify({
            'success': True,
            'extracted_text': text.strip(),
            'expected_text': 'Hello World! Test 123',
            'match': 'Hello World! Test 123' in text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'diagnostics': diagnose_tesseract()
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)