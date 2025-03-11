import os
import logging
import numpy as np
from flask import Flask, request, jsonify, render_template
from PIL import Image
import easyocr
import fitz  # PyMuPDF
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('flask_ocr.log')]
)

def extract_text_from_image(image_path):
    """Extract text from an image using EasyOCR"""
    try:
        img = Image.open(image_path)
        result = reader.readtext(np.array(img), detail=0, paragraph=True)
        return "\n".join(result)
    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extract text from the first page of a PDF using OCR"""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        result = reader.readtext(np.array(img), detail=0, paragraph=True)
        return "\n".join(result)
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    if file.filename.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = extract_text_from_image(file_path)
    
    return jsonify({"text": extracted_text})

if __name__ == '__main__':
    app.run(debug=True)
