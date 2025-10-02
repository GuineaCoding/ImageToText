from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import pytesseract
import subprocess
import os

app = Flask(__name__)

# Test Tesseract on startup
try:
    result = subprocess.run(['tesseract', '--version'], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("Tesseract is working!")
        print(f"Version: {result.stdout.strip()}")
        TESSERACT_WORKING = True
    else:
        print(f"Tesseract failed: {result.stderr}")
        TESSERACT_WORKING = False
except Exception as e:
    print(f"Tesseract error: {e}")
    TESSERACT_WORKING = False

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
        return jsonify({'error': 'OCR system is not ready. Please try again in a moment.'}), 500
    
    try:
        file_bytes = file.read()
        if len(file_bytes) == 0:
            return jsonify({'error': 'Empty file'}), 400
        
        # Open and process image
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Perform OCR
        text = pytesseract.image_to_string(img, config='--psm 6')
        
        return jsonify({'text': text.strip()})
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy' if TESSERACT_WORKING else 'unhealthy',
        'tesseract_working': TESSERACT_WORKING,
        'service': 'TextExtract Pro'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)