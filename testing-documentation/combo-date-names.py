import boto3
import time
import pandas as pd
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from tqdm import tqdm  # Import the tqdm library for progress bar

# Ask the user for the location of the credentials.txt file
credentials_file_path = input("Enter the path to the credentials.txt file: ")

# Read AWS credentials and S3 bucket name from the provided file path
with open(credentials_file_path, 'r') as file:
    credentials = file.readlines()

aws_access_key_id = None
aws_secret_access_key = None
s3_bucket_name = None

for line in credentials:
    if line.startswith('AWS_ACCESS_KEY_ID='):
        aws_access_key_id = line.split('=')[1].strip()
    elif line.startswith('AWS_SECRET_ACCESS_KEY='):
        aws_secret_access_key = line.split('=')[1].strip()
    elif line.startswith('S3_BUCKET_NAME='):
        s3_bucket_name = line.split('=')[1].strip()

if aws_access_key_id is None or aws_secret_access_key is None or s3_bucket_name is None:
    raise ValueError("Invalid credentials in credentials.txt file")

# AWS region
aws_region = "us-east-2"  # Replace with your desired region

# Amazon Textract client
textract = boto3.client('textract', region_name=aws_region)

# Create an S3 client
s3_client = boto3.client('s3', region_name=aws_region)

# Initialize NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

us_states_list = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina',  'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']  # Add all US state names

# Retrieve the list of objects in the S3 bucket
response = s3_client.list_objects_v2(Bucket=s3_bucket_name)
progress_bar = tqdm(total=len(response.get('Contents', [])), desc="Processing")

# Create an empty list to store the extracted text data
data = []

# Iterate over the objects in the bucket
for obj in response.get('Contents', []):
    # Get the object key
    object_key = obj.get("Key")

    if object_key:
        try:
            response = textract.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': s3_bucket_name,
                        'Name': object_key
                    }
                }
            )

            # Get the JobId for the document analysis job
            job_id = response['JobId']

            # Poll for the completion of the document analysis job
            while True:
                response = textract.get_document_text_detection(JobId=job_id)

                status = response['JobStatus']
                if status in ['SUCCEEDED', 'FAILED']:
                    break

                time.sleep(5)  # Wait for 5 seconds before polling again

            if status == 'SUCCEEDED':
                # Get the results of the document analysis job
                blocks = response['Blocks']

                # Extract text from each block
                text = ''
                for block in blocks:
                    if block['BlockType'] == 'LINE':
                        text += block['Text'] + '\n'

                # Tokenize the text into words and sentences
                words = word_tokenize(text)
                sentences = sent_tokenize(text)

                # Perform NLP analysis and corrections here
                # For example, you can use named entity recognition or context-based rules

                # Initialize TextBlob with the text
                blob = TextBlob(text)

                # Extract dates, proper names and entities, and US states
                dates = [item[0] for item in blob.noun_phrases if item[0].isdigit()]
                proper_names_entities = [item[0] for item in blob.tags if item[1] in ['NNP', 'NNPS']]
                us_states = [state for state in blob.words if state.lower() in us_states_list]  # us_states_list is a list of US state names

                # Join the lists into strings
                dates_str = ', '.join(dates)
                proper_names_entities_str = ', '.join(proper_names_entities)
                us_states_str = ', '.join(us_states)

                # Append the extracted data to the data list
                data.append({'File Title': object_key, 'Text': text, 'Dates': dates_str,
                             'Proper Names and Entities': proper_names_entities_str, 'US States': us_states_str})
        except Exception as e:
            print(f"Error processing {object_key}: {str(e)}")
            continue

        # Update the progress bar
        progress_bar.update(1)

# Close the tqdm progress bar
progress_bar.close()

# Convert the data list to a pandas DataFrame
df = pd.DataFrame(data)

# Save the cleaned text data to an Excel file
excel_file = 'text_data.xlsx'
df.to_excel(excel_file, index=False)
print(f"Text data saved to {excel_file}")
