import os
import fitz  # PyMuPDF library
from PIL import Image
from pytesseract import pytesseract

def pdf_to_text(pdf_path, text_path):
    # Extract text from a PDF file and save it to a .txt file using OCR
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_pixmap()

        # Convert PDF page to image (PNG)
        image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)

        # Perform OCR on the image
        page_text = pytesseract.image_to_string(image, lang='eng')  # You can specify the language as needed

        text += page_text

    with open(text_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)

def process_pdfs(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            text_filename = filename.replace('.pdf', '.txt')

            text_path = os.path.join(folder_path, text_filename)

            # Convert PDF to text using OCR and save it as a separate .txt file
            pdf_to_text(pdf_path, text_path)
            print(f"Processed {filename}")

# Specify the folder containing your PDFs
folder_path = r'G:\Carl Albert Collection' #Paste the directory path here
process_pdfs(folder_path)
