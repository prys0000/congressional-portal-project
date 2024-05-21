import openai
import os
import re
import time
import dateparser  # You may need to install this library for date parsing
from dateparser import parse as dateparser_parse
import spacy  # You may need to install spaCy for named entity recognition
import pandas as pd
import sys
from collections import defaultdict
import nltk
from nltk.stem import PorterStemmer
from dateutil.parser import parse as dateparser_parse

# Initialize stemmer
stemmer = PorterStemmer()

sys.setrecursionlimit(10000)  # Set a higher value than the default

# Set your OpenAI API key here
openai.api_key = "ADD API KEY"

# Define the directory containing .txt files
input_directory = "ADD PATH"  # Replace with the directory containing your .txt files

# Initialize the OpenAI API client
OpenAI.api_key = openai.api_key

# Initialize spaCy NLP model for named entity recognition
nlp = spacy.load("en_core_web_sm")

# Define global variables and settings
DELAY_BETWEEN_REQUESTS = 1  # Delay in seconds between API calls
MAX_RETRIES = 3  # Maximum number of retries for API calls
RETRY_DELAY = 5  # Delay in seconds before retrying an API call

# Global definition of predefined tribes - EACH SECTION BELOW HAS CENTER SPECIFIC DICTIONARIES - ADD YOUR OWN AND ADJUST THE TEMPLATE (LEAVING THE FIRST COUPLE FOR EXAMPLES)
predefined_tribes = [
    'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 
    'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Comanche', 

]

tribal_leaders_mapping = {
    'Seminole Indians': ['Coeehajo', 'George Harjo', 'Floyd Harjo', 'Richmond Tiger', 'Leonard Harjo', 'Lewis Johnson', 'Lewis J. Johnson', 'Alice Brown', 'Alice brown davis', 'Chili Fish', 'Chief Fish', 'George Jones', 'Chief George Jones', 'Willie Haney', 'Chief Haney', 'Jeffie Brown', 'Marci Cully', 'Chief Cully', 'Phillip Walker', 'Chief walker', 'John A. Brown', 'Terry Walker', 'Chief Harjo', 'Edwin Tanyan', 'Chief Tanyan', 'Tom Palmer', 'James Milam', 'Jerry Haney', 'Kenneth Chambers', 'Emarthale', 'Enoch Kelly Haney', 'Leonard M. Harjo'],
    'Cherokee Indians': ['W.W. Keeler', ' Bill Keeler', 'William Keeler', 'Ross Swimmer', ' Ross O. Swimmer', 'Wilma Mankiller', 'William Hicks', 'John Ross', 'Big Tiger', 'Pathkiller', 'John Jolly', 'Nimrod Smith', 'Sampson Owl', 'John Tahquette', 'Jarret Blythe', 'Robert Youngdeer', 'Frank Boudinot', 'W.W. Keeler', 'WW Keeler', 'JB Milan', 'J.B. Milan', 'Chuck Hoskin'],
}

# Invert the mapping to create a leader-to-tribe mapping
leader_to_tribe_mapping = {leader: tribe for tribe, leaders in tribal_leaders_mapping.items() for leader in leaders}


# Pre-processing function
def preprocess_text(text):
    # Simple preprocessing steps to remove special characters and lowercase the text
    text = text.lower()
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    # Optionally, add spell correction or other preprocessing steps here
    return text

# Post-processing function for the summary
def postprocess_text(text):
    # Further cleaning if necessary
    text = re.sub(r'\s+', ' ', text).strip()  # Collapse multiple spaces and trim
    return text

# Create empty lists to store data - CREATE YOUR LISTS (COLUMNS-DATA POINTS)
filenames = []  # Define the filenames list

summaries = []  # Define the summaries list

creators = []  # List to store creators

recipients = []  # List to store recipients

subjects_list = []  # Define the subjects list

dates_list = []  # Define the dates list

named_entities_list = []  # Define the named entities list

states_list = []  # Define the states list

tribes_list = []  # Define the tribes list

policies_list = []  # Define the policies list

parties_list = []  # Define the parties list

titles_list = []  # Define the titles list

tribal_organizations_list = []

congress_list = []

tribal_leaders_list = []


# Function to simplify titles
def simplify_title(title):
    # Define patterns to match titles like "Congressman James R. Jones"
    title_patterns = [
        r'Congressman\s+([A-Z][a-z]+(\s+[A-Z][a-z]+)*)',
        r'Representative\s+([A-Z][a-z]+(\s+[A-Z][a-z]+)*)',
    ]

    for pattern in title_patterns:
        match = re.search(pattern, title)
        if match:
            name = match.group(1).strip() if match.group(1) else None
            if name:
                return name  # Return the simplified name

    return title  # Return the original title if no match

def generate_title(text):
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.chat.completions.create(
                model="add MODEL",
                messages=[{"role": "user", "content": f"Create a title for the following text:\n{text}"}  # User message includes the prompt
                ],
                max_tokens=35, #DEFINE YOUR TOKEN/LIMITS
                n=1,
                stop=None,
                temperature=0.7 #ADD YOUR OWN FOCUS
            )
            last_choice = response.choices[-1]  # Get the last choice object
            last_message_content = last_choice.message.content  # Access the 'content' attribute of the 'message' object
            return last_message_content.strip()
        except openai.APIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API request failed, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise e

# Function to generate a summary using ChatGPT with retry handling
def generate_summary(text, max_summary_length=200): #ADD YOUR OWN LENGTH
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.chat.completions.create(
                model="ADD MODEL", #ADD YOUR MODEL IF NEEDED, OTHERWISE DELETE
                messages=[{"role": "user", "content": f"Summarize the following text:\n{text}\nSummary:"}],
                max_tokens=max_summary_length,
                n=1,
                stop=None,
                temperature=0.7
            )
            last_choice = response.choices[-1]  # Get the last choice object
            last_message_content = last_choice.message.content  # Access the 'content' attribute of the 'message' object
            return last_message_content.strip()
        except openai.APIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API request failed, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise e

def analyze_summary(summary): #USE YOUR PREFERRED MODEL (nlp)
    # Convert the summary text into a spaCy document object
    doc = nlp(summary)

    # Initialize creator and recipient
    creator = None
    recipient = None
    
    # Identify named entities and their roles #ADJUST YOUR OWN DATA POINTS (OURS IS FOCUSED ON COMMUNICATIONS)
    for ent in doc.ents:
        if ent.label_ == "PERSON":  # Check if the entity is a person
            prev_token = doc[ent.start - 1].lower_ if ent.start > 0 else ''
            next_token = doc[ent.end].lower_ if ent.end < len(doc) else ''
            
            # Check the tokens around the person entity for roles
            if prev_token in ["from", "by", "mr.", "mrs.", "ms.", "dr."] or next_token in ["writes", "wrote"]:
                creator = ent.text
            elif prev_token in ["to", "urging"] or "response" in ent.sent.text.lower():
                recipient = ent.text

    # If both are not identified, use heuristic based on the order they appear
    if not creator or not recipient:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if not creator:
                    creator = ent.text
                elif not recipient:
                    recipient = ent.text
                if creator and recipient:
                    break

    return creator, recipient


# Lists for storing additional data
creators = []
recipients = []
summaries = []

# Function to assign subjects to transcripts based on keywords
def assign_subjects(transcript, max_subjects=3): #USE LOC SUBJECT HEADINGS BUT MAKE SURE TO MAP THE RELATIONSHIPS THAT ARE COMMON BUT NOT DUPLICATED AND RECIPROCAL ELEMENTS BELOW
    keyword_subject_mapping = {
        		'Abortion--Law and legislation--United States': ['pro-choice', 'pro-life', 'reproductive rights', 'family planning', 'roe v. wade', 'planned parenthood', 'heartbeat bill', 'medical abortion', 'surgical abortion', 'elective abortion', 'therapeutic abortion', 'national right to life', 'sex education', 'birth control', 'roe vs. wade', 'roe v wade'],
				'Advertising, Political--United States': ['campaign advertisement',  'campaign commercial', 'political media', 'propaganda',  'political campaign communication', 'advertising', 'television ad', 'radio ad', 'associated press', 'press corp'],
				        
    }

    assigned_subjects = []
    transcript_lower = transcript.lower()  # Convert transcript to lowercase

    # Create a dictionary to count keyword matches for each subject
    subject_keyword_matches = defaultdict(int)

    for subject, keywords in keyword_subject_mapping.items():
        for keyword in keywords:
            # Use stemmed version of keywords for broader matching
            stemmed_keyword = stemmer.stem(keyword.lower())
            if stemmed_keyword in transcript_lower:
                subject_keyword_matches[subject] += transcript_lower.count(stemmed_keyword)

    # Sort subjects by the number of keyword matches and limit the number of assigned subjects
    for subject, _ in sorted(subject_keyword_matches.items(), key=lambda item: item[1], reverse=True)[:max_subjects]:
        assigned_subjects.append(subject)

    return assigned_subjects
    
# Function to extract tribes from text
def extract_tribes(text): #ADD YOUR OWN DICTIONARY AND ADJUST DATA TO MATCH PREDEFINITIONS ABOVE
    # Define the list of predefined _______ # ADD
    predefined_#add = [

    ]
    
    # Convert the text to lowercase to ensure case-insensitive matching
    text_lower = text.lower()
    
    # Initialize an empty list to store extracted tribes
    extracted_tribes = []
    
    # Iterate through predefined tribes and check if they exist in the text
    for _____ #ADD in predefined_#add:
        # Check if the _____#add name is in the text (case-insensitive)
        if #ADD.lower() in text_lower:
            extracted_#add.append(#add)

    return extracted_#add


# Function to extract tribal organizations from extracted tribes #LEFT THIS AS AN EXAMPLE THAT THE MODEL IF MATCHED TO THE PREDEFINED LIST WILL CHECK FOR THIS SECTION AS WELL - MUST MATCH OR %99.99 RELATED TO EXTRACT
def extract_tribal_organizations(extracted_tribes_.9999*/*/C/R):
    # Define a mapping of tribes to tribal organizations
    tribal_organizations_mapping = {
        'Seminole Indians': ['Coeehajo', 'George Harjo', 'Floyd Harjo', 'Richmond Tiger', 'Leonard Harjo', 'Lewis Johnson', 'Lewis J. Johnson', 'Alice Brown', 'Alice brown davis', 'Chili Fish', 'Chief Fish', 'George Jones', 'Chief George Jones', 'Willie Haney', 'Chief Haney', 'Jeffie Brown', 'Marci Cully', 'Chief Cully', 'Phillip Walker', 'Chief walker', 'John A. Brown', 'Terry Walker', 'Chief Harjo', 'Edwin Tanyan', 'Chief Tanyan', 'Tom Palmer', 'James Milam', 'Jerry Haney', 'Kenneth Chambers', 'Emarthale', 'Enoch Kelly Haney', 'Leonard M. Harjo'],
     }    
    
    tribal_organizations = []

    # Iterate through extracted tribes and map them to organizations
    for tribe in extracted_tribes:
        if tribe in tribal_organizations_mapping:
            tribal_organizations.extend(tribal_organizations_mapping[tribe])

    # Remove duplicates and return as a list
    return list(set(tribal_organizations))
    
def find_and_tag_tribal_leaders(text):
    # Initialize a list to store the found leaders and their tribes
    found_leaders_with_tribes = []

    # Convert the text to lowercase to improve matching reliability
    text_lower = text.lower()

    # Check if a leader's name is in the text
    for leader, tribe in leader_to_tribe_mapping.items():
        if leader.lower() in text_lower:
            # If the leader is found, append both the leader's name and their tribe to the list
            found_leaders_with_tribes.append((leader, tribe))

    return found_leaders_with_tribes


# Function to extract dates from text
def extract_dates(text):
    # Regular expression pattern to match various date formats
    date_pattern = r'(\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2}, \d{4}|\b(?:19[89][7-9]|20[01][0-9])\b))'

    # Find all date matches in the text using the pattern
    date_matches = re.findall(date_pattern, text)

    # Remove duplicates and return as a list
    formatted_dates = list(set(date_matches))

    return formatted_dates

# Function to extract named entities from text using spaCy
def extract_named_entities(text):
    doc = nlp(text)
    named_entities = [ent.text for ent in doc.ents]
    return named_entities

# Function to extract states from text using spaCy NER
def extract_states(text):
    doc = nlp(text)
    recognized_states = set()
    
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            recognized_states.add(ent.text)
            
    # Define a list of recognized countries to exclude them
    recognized_countries = set([
        "United States", "Canada", "Mexico", "Argentina", "London", "England", "Japan", "China"])
    
    # Filter out recognized countries from the recognized states
    filtered_states = [state for state in recognized_states if state not in recognized_countries]
    
    return filtered_states
    
# Function to assign policies from list   
def assign_policy(summary, text): #ADD YOUR POLICIES (FOR PORTAL) BUT DEFINE THE RELATIONSHIPS + ADD RECIPROCAL FUNCTIONS - OR ADD NEW LISTS
    global predefined_tribes
    predefined_policies = {
        'Agriculture and Food': ['US Department of Agriculture ', 'USDA', 'Food and Drug Administration'], 
        'Animals': ['endangered species', 'animal welfare', 'marine protection', 'animal cargo', 'Exotic Wildlife', 'Animal Abuse', 'Animal Rights'], 
      }
    
    # Ensure summary and text are lowercase for a case-insensitive search
    summary_lower = summary.lower()
    text_lower = text.lower()

    # Initialize an empty set to store unique matching policies
    matching_policies = set()

    # Check if any predefined policy keywords are in the summary or the text
    for policy, keywords in predefined_policies.items():
        for keyword in keywords:
            if keyword in summary_lower or keyword in text_lower:
                matching_policies.add(policy)

    if matching_policies:
        return list(matching_policies)
    else:
        return ['No Policy Assigned']  # Default assignment if no policy is matched

# Function to assign party affiliation based on summary content
def assign_party(summary): #ADD PARTIES OR DEFINE NEW LIST
    predefined_parties = {
        'Independence Party': ['independence party'],
        'Alliance Party': ['alliance party'],
        'American Independent Party': ['american independent party'],
       
    }
    
    summary_lower = summary.lower()
    found_parties = []
    
    # Iterate through predefined parties and check for keywords
    for party, keywords in predefined_parties.items():
        for keyword in keywords:
            if keyword in summary_lower:
                found_parties.append(party)
                break  # Break out of the inner loop if a keyword is found
    
    # Return the list of found parties or a default value if the list is empty
    return found_parties or ['No Party Assigned']

# Function to map dates to congress year ranges
def map_date_to_congress(date): #ADD CONGRESSES FOR FILTERING OR ADD NEW LIST
    # Define the congresses and their corresponding date ranges
    congresses = {
        '50th Congress (1887-1889)':   ('1887-3-04', '1889-3-03'),
        '51st Congress (1889-1891)':   ('1889-3-04', '1891-3-03'),
        '52nd Congress (1891-1893)':   ('1891-3-04', '1893-3-03'),
        '53rd Congress (1893-1895)':   ('1893-3-04', '1895-3-03'),

    }
    
    # Initialize a set to store unique congresses
    unique_congresses = set()

    # Convert each date to a datetime object and map to a congress
    for date in dates:
        date = dateparser_parse(date)
        for congress, (start_date, end_date) in congresses.items():
            start_date = dateparser_parse(start_date)
            end_date = dateparser_parse(end_date)
            if start_date <= date <= end_date:
                unique_congresses.add(congress)
                break  # Stop searching for congresses once a match is found

    # Convert the set of unique congresses to a list
    congress_list = list(unique_congresses)

    return congress_list


# Iterate through .txt files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Introduce a delay before making each API call
        time.sleep(DELAY_BETWEEN_REQUESTS)

        # Generate a title using ChatGPT
        title = generate_title(content)
        
        # Generate a summary using ChatGPT
        summary = generate_summary(content)
		
		# Analyze the summary
        creator, recipient = analyze_summary(summary)
             
        # Generate policy assignment
        policy = assign_policy(summary, content)
        
        # Generate party assignment
        party = assign_party(summary)
        
        # Extract tribal organizations based on extracted tribes
        tribal_organizations = extract_tribal_organizations(content)

        # Extract dates, named entities, and states
        states = extract_states(content)
        dates = extract_dates(content)
        named_entities = extract_named_entities(content)
        extracted_tribes = extract_tribes(content)
            
        # Assign subjects to the transcript
        assigned_subjects = assign_subjects(content)
        
        # Find and tag tribal leaders with their tribes
        found_leaders_with_tribes = find_and_tag_tribal_leaders(content)

        # Append data to lists
        filenames.append(filename)
        titles_list.append(title)
        summaries.append(summary)
        creators.append(creator)
        recipients.append(recipient)
        subjects_list.append(assigned_subjects)
        tribes_list.append(extracted_tribes)
        dates_list.append(dates)
        named_entities_list.append(named_entities)
        states_list.append(states)
        policies_list.append(policy)  # Append the assigned policy
        parties_list.append(party)  # Append the assigned party
        tribal_organizations_list.append(tribal_organizations)
        tribal_leaders_list.append(found_leaders_with_tribes)

# Create a DataFrame
data = {
    'Filename': filenames,
    'Title': titles_list,
    'Summary': summaries,
    'Creator': creators,
    'Recipient': recipients,
    'Subjects': subjects_list,
    'Tribes': tribes_list,
    'Dates': dates_list,
    'Named Entities': named_entities_list,
    'States': states_list,  # Added missing comma here
    'Policies': policies_list,  # Added missing comma here
    'Parties': parties_list,
    'Tribal Organizations': tribal_organizations_list,  # Add this line
    'Tribal Leaders': tribal_leaders_list
}

df = pd.DataFrame(data)

df['Congress'] = df['Dates'].apply(lambda dates: map_date_to_congress(dates))

# Export to Excel
output_excel_file = r"G:\Test_Folder\TEst_1_5-7-2024\txt\transcript_info.xlsx"
df.to_excel(output_excel_file, index=False)

print(f"Data saved to {output_excel_file}")
