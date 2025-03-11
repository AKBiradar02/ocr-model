import easyocr
import numpy as np
import cv2
import fitz  # PyMuPDF
from PIL import Image
import io

reader = easyocr.Reader(['en'], gpu=True)

def process_image(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        return extract_text_from_image(file_path)

def extract_text_from_image(image):
    """Extract text from an image file path or a PIL Image object."""
    if isinstance(image, str):  # If it's a file path
        img = Image.open(image)
    else:  # If it's an image object (from PDF processing)
        img = image

    result = reader.readtext(np.array(img), detail=0, paragraph=True)
    return "\n".join(result)

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        return extract_text_from_image(img)  # Pass the PIL Image object
    except Exception as e:
        return str(e)
