from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
import io
import os

app = Flask(__name__)

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Open image
        img = Image.open(io.BytesIO(file.read()))
        
        # Perform OCR with configuration
        custom_config = r'--oem 3 --psm 6'  
        text = pytesseract.image_to_string(img, config=custom_config)
        
        return jsonify({'text': text.strip()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/about')
def about():
    return render_template('about.html')
if __name__ == '__main__':
    app.run(debug=True) 