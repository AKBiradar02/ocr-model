from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import jwt
import datetime
from functools import wraps
import numpy as np
import logging
import io
from PIL import Image
import easyocr
import fitz  # PyMuPDF
import uuid
import bcrypt
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('flask_ocr.log')]
)

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize EasyOCR reader - set gpu=False if you don't have GPU support
reader = easyocr.Reader(['en'], gpu=False)

users = []
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')

if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, 'r') as f:
            users_data = json.load(f)
            for user in users_data:
                if isinstance(user['password'], str):
                    user['password'] = user['password'].encode('utf-8')
            users = users_data
    except Exception as e:
        logging.error(f"Error loading users: {str(e)}")


def save_users():
    try:
        users_data = []
        for user in users:
            user_copy = user.copy()
            if isinstance(user_copy['password'], bytes):
                user_copy['password'] = user_copy['password'].decode('utf-8')
            users_data.append(user_copy)
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f)
    except Exception as e:
        logging.error(f"Error saving users: {str(e)}")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((user for user in users if user['id'] == data['id']), None)
            if current_user is None:
                return jsonify({'message': 'User not found!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def extract_text_from_image(image_path):
    """Extract text from an image using EasyOCR"""
    try:
        img = Image.open(image_path)
        result = reader.readtext(np.array(img), detail=0, paragraph=True)
        if not result:
            return "No text detected in the image."
        return "\n".join([str(r) for r in result])
    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}")
        return f"Error processing image: {str(e)}"


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using PyMuPDF and EasyOCR"""
    try:
        doc = fitz.open(pdf_path)
        text_results = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Get a pixmap (image) of the page
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Process with EasyOCR
            result = reader.readtext(np.array(img), detail=0, paragraph=True)
            if result:
                text_results.extend(result)
        
        doc.close()
        
        if not text_results:
            return "No text detected in the PDF."
            
        return "\n".join([str(r) for r in text_results])
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return f"Error processing PDF: {str(e)}"


# Routes
@app.route('/')
def home():
    return jsonify({'message': 'OCR API is running'})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['name', 'email', 'password']):
        return jsonify({'message': 'Missing required fields!'}), 400
        
    if any(user['email'] == data['email'] for user in users):
        return jsonify({'message': 'User already exists!'}), 400
        
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = {'id': str(uuid.uuid4()), 'name': data['name'], 'email': data['email'], 'password': hashed_password}
    users.append(new_user)
    save_users()
    return jsonify({'message': 'User created successfully!'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': 'Email and password are required!'}), 400
        
    user = next((user for user in users if user['email'] == data['email']), None)
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        token = jwt.encode(
            {'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, 
            app.config['SECRET_KEY'], 
            algorithm="HS256"
        )
        return jsonify({
            'token': token, 
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
        })
    return jsonify({'message': 'Invalid credentials!'}), 401


@app.route('/api/ocr', methods=['POST'])
@token_required
def ocr(current_user):
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request!'}), 400
        
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'message': 'No file selected!'}), 400
        
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'message': 'File type not allowed!'}), 400
        
    # Save file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process image or PDF based on file type
    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)
    
    # Clean up - remove the file after processing
    try:
        os.remove(file_path)
    except Exception as e:
        logging.error(f"Error removing file: {str(e)}")
    
    return jsonify({'text': text})


@app.route('/api/ocr/public', methods=['POST'])
def public_ocr():
    """Public OCR endpoint that doesn't require authentication"""
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request!'}), 400
        
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'message': 'No file selected!'}), 400
        
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'message': 'File type not allowed!'}), 400
        
    # Save file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process image or PDF based on file type
    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)
    
    # Clean up - remove the file after processing
    try:
        os.remove(file_path)
    except Exception as e:
        logging.error(f"Error removing file: {str(e)}")
    
    return jsonify({'text': text})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
