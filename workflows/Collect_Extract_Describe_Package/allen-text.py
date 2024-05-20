"""
PDF Processing App

Instructions:
1. Install dependencies using pip install -r requirements.txt
2. Set up AWS credentials:
   - Create a custom credentials file and specify its path in custom_credentials_file variable.
   - Ensure that your AWS credentials are configured properly (e.g., AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
3. Run the script using python pdf_processing_app.py
"""

import boto3
import os
import time
from openpyxl import Workbook
import fitz  # PyMuPDF

# Path to your custom credentials file
custom_credentials_file = r"add your credentials path.txt"

# Set the AWS_SHARED_CREDENTIALS_FILE environment variable
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = custom_credentials_file

# Define AWS services
s3_client = boto3.client('s3')
textract_client = boto3.client('textract', region_name='set your region')  # Replace with your region

# Define the bucket name and local directories
bucket_name = 'add your bucket name'
local_dir = "add your path to folder txt will go"
os.makedirs(local_dir, exist_ok=True)

# Define list to hold data for Excel
excel_data = []

# List PDF files from the S3 bucket
response = s3_client.list_objects_v2(Bucket=bucket_name)

# Process files if the bucket is not empty
if 'Contents' in response:
    for item in response['Contents']:
        file_name = item['Key']
        if file_name.endswith('.pdf'):
            print(f"Processing file: {file_name}")

            # Start Textract job to process the PDF file
            textract_response = textract_client.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': file_name
                    }
                }
            )

            # Get the job ID from Textract response
            job_id = textract_response['JobId']
            print(f"Started job with id: {job_id}")

            # Poll Textract job for status
            while True:
                result = textract_client.get_document_text_detection(JobId=job_id)
                status = result['JobStatus']
                if status == 'SUCCEEDED':
                    print(f"Textract job succeeded for {file_name}")
                    break
                elif status == 'FAILED':
                    print(f"Textract job failed for {file_name}")
                    break
                print("Waiting for Textract job to complete...")
                time.sleep(5)

            # Process text block from Textract response
            if status == 'SUCCEEDED':
                text_content = []
                blocks = result.get('Blocks', [])
                for block in blocks:
                    if block['BlockType'] == 'LINE':
                        text_content.append(block['Text'])

                # Save text content to a file
                output_file_path = os.path.join(local_dir, os.path.splitext(file_name)[0] + '.txt')
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    for line in text_content:
                        f.write(line + '\n')
                print(f"Text output saved to {output_file_path}")

                # Download the PDF temporarily to extract its dimensions and size
                temp_pdf = os.path.join(local_dir, file_name)
                s3_client.download_file(bucket_name, file_name, temp_pdf)

                # Check if the downloaded PDF file exists
                if os.path.exists(temp_pdf):
                    pdf_document = fitz.open(temp_pdf)
                    num_pages = len(pdf_document)
                    page = pdf_document[0]
                    width, height = page.rect.width, page.rect.height
                    file_size = os.path.getsize(temp_pdf)
                    pdf_document.close()

                    # Remove the temporary PDF file
                    os.remove(temp_pdf)

                    # Append file info to the excel data list
                    excel_data.append((file_name, num_pages, width, height, file_size))

# Create a new Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "PDF Info"

# Add headers to the worksheet
headers = ['Filename', 'Number of Pages', 'PDF Width', 'PDF Height', 'File Size']
ws.append(headers)

# Add data to the worksheet
for row in excel_data:
    ws.append(row)

# Save the Excel file
output_excel_file = os.path.join(local_dir, 'technical_counts_info.xlsx')
wb.save(output_excel_file)
print(f"Combined information saved to {output_excel_file}")
