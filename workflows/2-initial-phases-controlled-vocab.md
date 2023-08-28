# **Initial Phases**

In the commencement stages of our project, the Carl Albert Center embarked on foundational decisions and preparatory work, which was integral to the systematic progression of the venture.

## Controlled Vocabulary

Creation of the controlled lists has been a comprehensive collection of legacy terminology, political science terminology, standardized common terms, controlled subject and political science policy guides, and standardized data management concepts. 

### Resources:
* Field Values (Political Science Resources):
    * [Policy Areas — Field Values](https://www.congress.gov/help/field-values/policy-area)
    * [Policy Areas by Congress](https://www.congress.gov/browse/policyarea/116th-congress)
    * [Congressional Record Index](https://www.congress.gov/congressional-record/congressional-record-index)
    * [LIV – Legislative Indexing Vocabulary](https://www.congress.gov/browse/legislative-indexing-vocabulary/106th-congress)
    * [Bills by Subject and Policy Area](https://www.congress.gov/help/find-bills-by-subject)
    * [ICPSR Datasets](https://oucac.access.preservica.com/index.php/icpsr-political-commercial-collection-coding/)
* Dates of Sessions of the Congress:
    * [List of all Sessions - 1789-present](https://history.house.gov/Institution/Session-Dates/All/)
* Subject headings, topics - Political Science:
    * [Library of Congress](https://id.loc.gov/authorities/subjects/sh85104440.html)
    * [Scraped lists from LOC-Political Science Research guide](https://guides.loc.gov/political-science)
    * [Legislative Subject Terms — Field Values](https://www.congress.gov/help/field-values/legislative-subject-terms)
    * [Legislative Subject Terms](https://www.congress.gov/browse/legislative-subject-terms)

* Locations and Geographic Names:
    * [Getty Thesaurus of Geographic Names® Online](https://www.getty.edu/research/tools/vocabularies/tgn/index.html)

#

### Scraping resource websites, developing lists, and Python

Scrape political science subject websites and lists and compare them to find the best term can be created by using the following workflow:

1. Scrape the Websites: You will need to scrape the websites to extract the political science subject terms. For this, you can use libraries like requests to fetch the web page and beautifulsoup4 to parse the HTML and extract the terms.

2. Store Terms in Excel: After scraping the websites, you can store the terms in an Excel file. For this, you can use the pandas library.

3. Run Comparison Script: Compare the terms from different websites to find the best term. You can use the fuzzywuzzy library to find the terms that are similar and decide which one to keep as the main term and which ones to keep as sub-terms.

4. Create Comprehensive Excel Sheet: After comparing the terms and deciding which ones to keep, create a comprehensive Excel sheet with the final list of terms and sub-terms.

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Scrape the websites

# List of websites to scrape
websites = [
    'https://example.com/political-science-terms',
    'https://example.com/political-science-glossary'
]

# List to store the scraped terms
terms = []

# Loop through each website and scrape the terms
for website in websites:
    # Fetch the web page
    response = requests.get(website)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the terms from the web page
    # Note: You will need to customize this part for each website
    for term in soup.select('.term'):
        terms.append(term.text)

# Step 2: Store terms in Excel

# Create a pandas DataFrame from the list of terms
df = pd.DataFrame(terms, columns=['Term'])

# Save the DataFrame to an Excel file
df.to_excel('political_science_terms.xlsx', index=False)

print('Terms saved to political_science_terms.xlsx')
```
**Customize the script for the actual websites you are scraping as the structure of each website will be different**

Next:

Build a comparison script.

```python
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Read the input Excel file
input_file = 'path/to/your/input_file.xlsx'
df = pd.read_excel(input_file)

# Columns to compare and standardize
column_to_standardize = 'Column1'
reference_column = 'ReferenceColumn'

# Function to find the best match from the reference column
def find_best_match(value, reference_column_values):
    return process.extractOne(value, reference_column_values)[0]

# Get unique values from the reference column
reference_values = df[reference_column].unique()

# Iterate through the column to standardize
standardized_names = []
for name in df[column_to_standardize]:
    best_match = find_best_match(name, reference_values)
    standardized_names.append(best_match)

# Add the standardized names to a new column in the DataFrame
df['Standardized Names'] = standardized_names

# Save the updated DataFrame to a new Excel file
output_file = 'path/to/your/output_file.xlsx'
df.to_excel(output_file, index=False)

print(f"Standardized names saved to {output_file}")
```

**These processes can be duplicated and combined for each metadata or standardized element.**

Next, create a standardized list of relevant (Political Science Authors, Congressional Representatives, Senators, Other Political Entities) names and entities to add to the scripting above. 

This process uses a training dataset that we developed from the above codes of scrapes websites, common lists, ICPSR data, etc... This section performs the following task:

1. Train a Named Entity Recognition [(NER) model](https://github.com/topics/named-entity-recognition): The script trains a [spaCy NER model](https://spacy.io/universe/project/video-spacys-ner-model) using custom labels and training [data from a CSV file](https://github.com/prys0000/political-commercial-collection-archives/blob/main/controlled-vocab-datasets-models/Controlled%20Vocabs_Lists.xlsx). The training data is split into a training set and an evaluation set. The NER model is trained using the training set, and then the trained model is saved to disk.

2. Extract text from a PDF file, Excel file: The script uses the pdfplumber and openpxl libraries to extract text from specified files.

3. Extract named entities from the extracted text: The trained NER model is used to extract entities from the text extracted from the files.

4. Save the extracted named entities to a text file: 

**The extracted named entities and their corresponding labels are written to a text file.**

```python
import os
import pandas as pd
import spacy
import pdfplumber
from sklearn.model_selection import train_test_split
from spacy.training.example import Example
import random  # Add the import statement for the 'random' module

def train_model(nlp, train_examples):
    # Create an optimizer
    optimizer = nlp.begin_training()

    # Training loop
    for epoch in range(10):
        random.shuffle(train_examples)
        losses = {}
        # Batch examples and iterate over them
        for batch in spacy.util.minibatch(train_examples, size=8):
            nlp.update(batch, drop=0.5, sgd=optimizer, losses=losses)
        print("Epoch:", epoch, "Losses:", losses)

    return nlp


# Load the annotated data from the CSV file
data = pd.read_csv(r"D:\GITHUB\Practice\tv files\TRAINING DATASETS\ner_training_politicalscience.csv", encoding='latin-1')

# Split the data into training and evaluation sets
train_data, eval_data = train_test_split(data, test_size=0.2, random_state=42)

# Train the Named Entity Recognition (NER) model using the training data
nlp = spacy.blank("en")  # Create a blank spaCy model
ner = nlp.add_pipe("ner", name="my_ner")

# Add custom labels to the NER component
custom_labels = ['LOCATION_STATE', 'ORGANIZATION_AGENCY', 'POLITICAL_PARTY']

for label in custom_labels:
    ner.add_label(label)

# Convert the labels to the BILOU format
def to_bilou(annotations):
    bilou_annotations = []
    for label in annotations:
        if label in custom_labels:
            bilou_annotations.append(label)
        else:
            bilou_annotations.append('O')
    return bilou_annotations

# Convert the training data to spaCy format
train_examples = []
for _, annotations in train_data.iterrows():
    bilou_annotations = to_bilou(annotations['label'])
    entities = []
    start = 0
    for i, label in enumerate(bilou_annotations):
        if label != 'O':
            if i == 0 or bilou_annotations[i - 1] != label:
                start = i
            if i == len(bilou_annotations) - 1 or bilou_annotations[i + 1] != label:
                entities.append((start, i + 1, label))

    train_examples.append(Example.from_dict(nlp.make_doc(annotations['text']), {"entities": entities}))

# Initialize the model with the tok2vec component
nlp.initialize(lambda: train_examples)

# Define the optimizer and loss function
optimizer = nlp.begin_training()
losses = {}

# Train the NER model
nlp = train_model(nlp, train_examples)

# Save the trained model to a specific location
output_folder = r"D:\GITHUB\Practice\tv files\TRAINING DATASETS"
output_model_path = os.path.join(output_folder, "en_core_political_science_model")
nlp.to_disk(output_model_path)

# Load the trained model
nlp = spacy.load(output_model_path)

def extract_text_from_pdf(pdf_file_path):
    text = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_named_entities(pdf_file_path):
    text = extract_text_from_pdf(pdf_file_path)
    doc = nlp(text)
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]
    return named_entities

def save_to_txt(pdf_file_path, output_folder):
    named_entities = extract_named_entities(pdf_file_path)

    # Create the output .txt file path
    output_file_path = os.path.join(output_folder, "named_entities_output.txt")

    # Write the named entities to the .txt file
    with open(output_file_path, "w", encoding="utf-8") as txt_file:
        for entity, label in named_entities:
            txt_file.write(f"Entity: {entity}, Type: {label}\n")

if __name__ == "__main__":
    pdf_file_path = r"D:\GITHUB\Practice\tv files\TRAINING DATASETS\tv-sample-orig-scanned.pdf"
    output_folder = r"D:\GITHUB\Practice\tv files\TRAINING DATASETS"

    save_to_txt(pdf_file_path, output_folder)
```
The results will be similar to the [CAC NER Controlled List results.](https://raw.githubusercontent.com/prys0000/political-commercial-collection-archives/main/practice/radio%20documents/ner_training_politicalscience.csv)

Feel free to use the [cac_en_core_political_science_model](https://github.com/prys0000/political-commercial-collection-archives/tree/main/controlled-vocab-datasets-models/en_core_political_science_model) for getting started.

**Edit the above template to work with your project needs**

#

### Using your controlled vocabulary to standardize metadata information

1. With existing finding aid data (in csv or excel formats) by:

    * Running the [qc-1-neh.py](https://github.com/prys0000/political-commercial-collection-archives/blob/f89d80f02de2cf68aad494918a72e00c9b7495f7/practice/radio%20documents/qc-1-neh.py) script to compare controlled vocabulary from the NER results to existing or legacy finding aid data and create a new metadata sheet with cleaned information.
    * Develop clear data validation mechanisms for new metadata sheets by adding the following to existing scripts or run alone. This allows students and staff to select standardized terminology for collecting metadata.
```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
Apply Data Validation
wb = Workbook()
ws = wb.active

# Create a data validation rule
dv = DataValidation(type="list", formula1=f'"{",".join(controlled_vocab.values())}"', showDropDown=True)

# Assuming headers are in the first row
for col in ws.iter_cols(min_row=1, max_row=1):
    for cell in col:
        cell.data_validation = dv

# Save the dataframe back to excel
cleaned_excel_path = "cleaned_worksheet.xlsx"
df.to_excel(cleaned_excel_path, index=False)
```


