import os
import pandas as pd
import spacy
import time
import re
import fitz
from pathlib import Path
from spellchecker import SpellChecker
from spacy.matcher import Matcher


spell = SpellChecker()

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

start_time = time.time()

# Ask the user for input and output directories
input_directory = input("Please provide the path to the directory containing the PDFs and TXTs: ")
output_directory = input("Please provide the path to the directory where the output Excel file should be saved: ")


# Function to extract dates from text
def extract_dates(text):
    date_pattern = (r'\d{1,2}/\d{1,2}/\d{4}|'
                    r'\d{2}/\d{2}/\d{4}|'
                    r'\d{1,2}-\d{1,2}-\d{4}|'
                    r'\d{2}-\d{2}-\d{4}|'
                    r'[A-Z][a-z]+ \d{1,2}, \d{4}')
    return re.findall(date_pattern, text)


# Load predefined locations, entities, and persons from CSV
labels_df = pd.read_csv(r"E:\BERT_training\new_CAC_NER_trainingmodel.csv", encoding="utf-8")
locations_set = set(labels_df[labels_df['label'] == 'LOCATION']['text'].str.lower())
entities_set = set(labels_df[labels_df['label'] == 'ENTITY']['text'].str.lower())
persons_set = set(labels_df[labels_df['label'] == 'PERSON']['text'].str.lower())
superpacs_set = set(labels_df[labels_df['label'] == 'SUPERPAC']['text'].str.lower())
political_party_set = set(labels_df[labels_df['label'] == 'POLITICAL_PARTY']['text'].str.lower())
subject_set = set(labels_df[labels_df['label'] == 'SUBJECT']['text'].str.lower())


# Initialize the Matcher
matcher = Matcher(nlp.vocab)

# Add patterns based on CSV data
for person in persons_set:
    pattern = [{"LOWER": word.lower()} for word in person.split()]
    matcher.add("PERSON", [pattern])

for entity in entities_set:
    pattern = [{"LOWER": word.lower()} for word in entity.split()]
    matcher.add("ENTITY", [pattern])

for superpac in superpacs_set:
    pattern = [{"LOWER": word.lower()} for word in entity.split()]
    matcher.add("SUPERPAC", [pattern])

for party in political_party_set:
    pattern = [{"LOWER": word.lower()} for word in party.split()]
    matcher.add("POLITICAL_PARTY", [pattern])

for subject in subject_set:
    pattern = [{"LOWER": word.lower()} for word in subject.split()]
    matcher.add("SUBJECT", [pattern])

# Function to extract locations from text
def extract_locations(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]

def extract_superpacs(text):
    doc = nlp(text)
    matches = matcher(doc)
    superpacs = [doc[start:end].text for match_id, start, end in matches if nlp.vocab.strings[match_id] == "SUPERPAC"]
    return superpacs

# Function to extract entities and persons from text
def extract_entities_and_persons(text):
    doc = nlp(text)
    matches = matcher(doc)

    entities = []
    persons = []
    political_parties = []
    subjects = []

    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if string_id == "PERSON":
            persons.append(span.text)
        elif string_id == "ENTITY":
            entities.append(span.text)
        elif string_id == "POLITICAL_PARTY":
            political_parties.append(span.text)
        elif string_id == "SUBJECT":
            subjects.append(span.text)

    return entities, persons, political_parties, subjects  # Return two separate lists


# Define additional common terms to be excluded
common_stop_words = list(nlp.Defaults.stop_words)
common_terms = ["a", "s", "today", "tomorrow", "determined", "spoke", "better", "get", "gets", "right", "end", "ends",
                "begins", "begin", "crowd", "crowds", "discusses", "discuss", "discussing", "audio", "sound", "visual",
                "run", "win", "vote", "support", "oppose", "political", "campaign", "candidate", "election", "voter",
                "placard", "placards", "introduced", "ask", "asks", "asked", "animation", "animations", "narrator",
                "narrating",
                "etc.", "list", "know", "example", "?", "zoom", "man on the street", "desk",
                "graphic", "graphics", "photo", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
                "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "oh", "head", "ask", "#", "cu", "etc", "clip",
                "opens", "seated", "sitting", "music", "spot", "ends", "plug", "cand", "help", "helped", "helps",
                "attitude", "attitudes", "speaking", "speak", "speaks", "tells", "told", "tell", "telling", "shown",
                "discuss", "scene", "scenes", "shots", "voice", "voices", "background", "show", "shows", "pic", "heard",
                "quote", "tag", "including", "includes", "include", "detail", "details", "detailed", "interviewer",
                "interviewing", "clips", "talk", "talks", "ok", "different", "voiceover", "cand ", "says", "good",
                "people", "shot", "camera", "ad", "picture", "change", "future", "together", "results", "voice", "ect",
                "focus", "focuses", "song", "including", "include", "includes", "gave", "given", "give", "step",
                "steps", "thing", "things", "superimposed", "super imposed", "came", "come", "coming", "footage",
                "announcer", "anncr", "take", "takes", "like", "likes", "collage", "shorter", "shorter version", "the",
                "this", "that", "of", "for", "but", "I", "so", "to", "those", "there", "is", "it", "it's", "there",
                "there's", "their", "theirs", "on", "off", "into", "take", "reply", "yes", "no", "usual", "gone", "going", "with", "felt", "feeling", "feelings", "kind", "kindly", "kindness"]

# Create a custom stoplist by combining spaCy's default stop words and common terms
custom_stoplist = set(common_terms).union(nlp.Defaults.stop_words)


# Function to extract keywords and two-word phrases from text
def extract_keywords(text):
    doc = nlp(text)
    keywords = []

    for i in range(len(doc) - 1):
        token1, token2 = doc[i], doc[i + 1]

        if (
                token1.text.lower() not in custom_stoplist
                and token2.text.lower() not in custom_stoplist
                and (token1.dep_ == "conj" or token1.dep_ == "amod")
                and (token2.dep_ == "conj" or token2.dep_ == "amod")
                and not token1.text.lower().endswith('ing')
                and not token2.text.lower().endswith('ing')
        ):
            keywords.append(f"{token1.text} {token2.text}")

    for token in doc:
        if token.text.lower() not in custom_stoplist and not token.text.lower().endswith('ing'):
            keywords.append(token.text)

    return keywords

# Function to correct spelling in a given text
def correct_spelling(text):
    words = text.split()
    misspelled = spell.unknown(words)
    for word in misspelled:
        corrected_word = spell.correction(word)
        if corrected_word:  # Check if corrected_word is not None or empty
            text = text.replace(word, corrected_word)
    return text


# Use the user-defined directory for the PDFs and TXTs
pdf_directory = Path(input_directory)

# Define the path to the output Excel file
output_excel_file = Path(output_directory) / "metadata.xlsx"

file_names, all_dates, all_locations, all_entities, all_keywords = [], [], [], [], []
all_persons = []
all_superpacs = []
all_political_parties = []
all_subjects = []


for file in os.listdir(pdf_directory):
    full_path = os.path.join(pdf_directory, file)
    text = ""  # Initialize text for each file

    try:
        if file.endswith(".pdf"):
            pdf_document = fitz.open(full_path)
            text = "".join(page.get_text() for page in pdf_document)
            text = text.replace('\n\n', ' ')
        elif file.endswith(".txt"):
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
            text = text.replace('\n\n', ' ')

        text = correct_spelling(text)

        dates = extract_dates(text)
        locations = extract_locations(text)
        entities, persons, political_parties, subjects = extract_entities_and_persons(text)
        superpacs = extract_superpacs(text)
        keywords = extract_keywords(text)

        file_names.append(file)
        all_dates.append(dates)
        all_locations.append(locations)
        all_entities.append(entities)
        all_persons.append(persons)
        all_keywords.append(keywords)
        all_superpacs.append(superpacs)
        all_political_parties.append(political_parties)  # Append to the list
        all_subjects.append(subjects)

    except Exception as e:
        print(f"Error processing file '{file}': {e}")

# Create a DataFrame
metadata_df = pd.DataFrame({
    'File Name': file_names,
    'Dates': all_dates,
    'Locations': all_locations,
    'Entities': all_entities,
    'Persons': all_persons,
    'Political Parties': all_political_parties,  # Use the right list
    'Keywords': all_keywords,
    'Superpacs': all_superpacs,
    'Subjects': all_subjects,
})

# Ensure the output directory exists
output_directory = Path(output_directory)
output_directory.mkdir(parents=True, exist_ok=True)

# Save the DataFrame to the Excel file
metadata_df.to_excel(output_excel_file, index=False)

end_time = time.time()
print(f"Total processing time: {end_time - start_time:.2f} seconds")
