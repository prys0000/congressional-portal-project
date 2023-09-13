import os
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pdf2image import convert_from_path
import sys

BASE_PATH = os.path.dirname(os.path.abspath(sys.executable))
poppler_path = os.path.join(BASE_PATH, 'poppler-0.68.0', 'bin')
pytesseract.pytesseract.tesseract_cmd = os.path.join(BASE_PATH, 'Tesseract-OCR', 'tesseract.exe')


def preprocess_image(image):
    """Applies preprocessing techniques to enhance image for OCR."""
    # Rescale the image
    image = image.resize((2 * image.width, 2 * image.height), Image.BICUBIC)

    # Convert to grayscale
    image = image.convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    # Apply binarization
    threshold = 150
    image = image.point(lambda p: p > threshold and 255)

    # Reduce noise
    image = image.filter(ImageFilter.MedianFilter(3))

    return image

def pdf_to_images(pdf_path):
    try:
        return convert_from_path(pdf_path, poppler_path=poppler_path)
    except Exception as e:
        print(f"Error while converting PDF to image: {e}")
        sys.exit(1)


def ocr_images(images):
    results = []
    for image in images:
        preprocessed = preprocess_image(image)
        results.append(pytesseract.image_to_string(preprocessed))
    return ''.join(results)


def process_pdf_folder(pdf_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            images = pdf_to_images(pdf_path)
            ocr_result = ocr_images(images)

            output_filename = os.path.splitext(filename)[0] + '.txt'
            output_filepath = os.path.join(output_folder, output_filename)

            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(ocr_result)

if __name__ == "__main__":
    # Get user-defined folder paths
    PDF_FOLDER_PATH = input("Enter the path to the PDF folder: ").strip()
    OUTPUT_FOLDER_PATH = input("Enter the path to the output folder: ").strip()

    # Check if the provided folders exist
    if not os.path.exists(PDF_FOLDER_PATH):
        print(f"The folder {PDF_FOLDER_PATH} does not exist!")
        sys.exit(1)  # Use sys.exit() to exit with an error code

    # Process the PDFs
    process_pdf_folder(PDF_FOLDER_PATH, OUTPUT_FOLDER_PATH)
    print("Done OCR for all PDFs!")
