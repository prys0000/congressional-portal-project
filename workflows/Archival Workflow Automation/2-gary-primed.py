import openai
import os
import re
import time
import spacy
import pandas as pd
from collections import defaultdict
from dateparser import parse as dateparser_parse
from nltk.stem import PorterStemmer
import json
import logging

logging.basicConfig(filename="errors.log", level=logging.ERROR)


def batch_openai_requests(contents, batch_size=5):
    """
    Batches multiple OpenAI API requests by sending them in groups of batch_size.
    """
    batch_responses = []
    separator = '\n---\n'  # Define a separator to split the responses

    # Process contents in chunks of batch_size
    for i in range(0, len(contents), batch_size):
        batch = contents[i:i + batch_size]  # Take a batch of inputs
        
        # Create a single concatenated prompt
        batch_prompt = separator.join([f"Create a title for the following text:\n{content}" for content in batch])
        
        try:
            # Call OpenAI API with the concatenated batch prompt
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": batch_prompt}],
                max_tokens=1500,  # Adjust according to your needs
                n=1,
                temperature=0.7
            )
            
            # Split the responses based on the separator
            titles = response['choices'][0]['message']['content'].split(separator)
            batch_responses.extend([title.strip() for title in titles])
        
        except Exception as e:
            print(f"Error generating batch titles: {e}")
            batch_responses.extend([None] * batch_size)  # Append None for failed batch

    return batch_responses


# Main function
def main():
    # Initialize stemmer and spaCy NLP model for named entity recognition
    stemmer = PorterStemmer()
    nlp = spacy.load("en_core_web_sm")

    # Load config from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    # Use config to set input/output paths and API key
    input_directory = config['input_directory']
    output_excel_file = config['outputs']['2-gary-primed']
    openai.api_key = config['openai_api_key']

    # Set other constants from config
    DELAY_BETWEEN_REQUESTS = config['retry_settings']['delay_between_requests']
    MAX_RETRIES = config['retry_settings']['max_retries']
    RETRY_DELAY = config['retry_settings']['retry_delay']

    # Predefined lists and mappings
    predefined_tribes = [
        'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 
        'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Comanche', 
        'Creek', 'Delaware', 'Iowa', 'Kaw', 'Keetoowah', 'Kickapoo', 
        'Kiowa', 'Lenape', 'Miami', 'Modoc', 'Muscogee', 'Odawa', 
        'Osage', 'Otoe', 'Ottawa', 'Pawnee', 'Ponca', 'Potawatomi', 'Mescalero Apache', 
        'Potowatomie', 'Quapaw', 'Sac and Fox', 'Sauk', 'Seminole', 
        'Shawnee', 'Tonkawa', 'Wichita', 'Wyandot', 'Wyandotte', 'Chippewa', 'Chilocco', 'Navajo', 'Hopi', 'Menominee', 
    ]

    tribal_leaders_mapping = {
        'Seminole Indians': ['Coeehajo', 'George Harjo', 'Floyd Harjo', 'Richmond Tiger', 'Leonard Harjo', 'Lewis Johnson', 'Lewis J. Johnson', 'Alice Brown', 'Alice brown davis', 'Chili Fish', 'Chief Fish', 'George Jones', 'Chief George Jones', 'Willie Haney', 'Chief Haney', 'Jeffie Brown', 'Marci Cully', 'Chief Cully', 'Phillip Walker', 'Chief walker', 'John A. Brown', 'Terry Walker', 'Chief Harjo', 'Edwin Tanyan', 'Chief Tanyan', 'Tom Palmer', 'James Milam', 'Jerry Haney', 'Kenneth Chambers', 'Emarthale', 'Enoch Kelly Haney', 'Leonard M. Harjo'],
        'Cherokee Indians': ['W.W. Keeler', ' Bill Keeler', 'William Keeler', 'Ross Swimmer', ' Ross O. Swimmer', 'Wilma Mankiller', 'William Hicks', 'John Ross', 'Big Tiger', 'Pathkiller', 'John Jolly', 'Nimrod Smith', 'Sampson Owl', 'John Tahquette', 'Jarret Blythe', 'Robert Youngdeer', 'Frank Boudinot', 'W.W. Keeler', 'WW Keeler', 'JB Milan', 'J.B. Milan', 'Chuck Hoskin','James Gordon', 'James L. Gordon'],
        'Choctaw Nation': ['Harry J.W. Belvin', 'Hollis E. Roberts', 'Joseph Kincaid', 'Peter Folsom', 'Green McCurtain', 'William F. Semple', 'William Semple', 'William A. Durant', 'Harry Belvin', 'Gary Batton', 'Hollis Roberts', 'David Burrage', 'Richard Branam', 'Pierre Juzan', 'Isaac Folsom', 'Thomas Leflore', 'Nathaniel Folsom', 'Silas Fisher', 'George Harkins', 'George W. Harkins', 'Cornelius Mccurtain', 'George Folsom', 'David Mccoy', 'Nicholas Cochnauer', 'Alfred Wade', 'Tandy Walker', 'Basil Leflore', 'George Hudson', 'Samuel Garland', 'Peter Pitchlynn', 'Allen Wright', 'Coleman Cole', 'Isaac Levi Garvin', 'Isaac Garvin', 'Jackson Mccurtain', 'Chief Mccurtain', 'Edmund Mccurtain', 'Thompson Mckinney', 'Ben Smallwood', 'Jefferson Gardner', 'Green Mccurtain', 'Gilbert Wesley Dukes', 'Victor Locke', 'William Semple', 'William F. Semple', 'Ben Dwight', 'William Durant', 'Clark David Gardner', 'Hollis Roberts', 'Hollis E. Roberts', 'Gregory Pyle', 'Gregory E. Pyle', 'Chief Pyle', 'Gary Batton', 'Chief Batton'],
        'Chickasaw Indians': ['Overton James', 'Anoatubby', 'Charles W. Blackwell', 'William Byrd', 'James Logan Colbert', 'Levi Colbert', 'Winchester Colbert', 'Cyrus Harris', 'Maytubby', 'Palmer Mosely', 'Palmer S. Mosely', 'Benjamin Overton', 'Jonas Wolf', 'Jerry Imotichey', 'Henry Pratt', 'Imotichey', 'Juanita Tate'],
        'Creek Indians': ['Claude Cox', 'Norman Hoyt', 'Robert L. Thomas', 'Gerald W. Hill', 'Samuel Chocote', 'Locher Harjo', 'Ward Coachman', 'Joseph M. Perryman', 'Legus Perryman', 'Edward Bullette', 'Sparhecher', 'Pleasant Porter', 'William McIntosh', 'Jim Pepper', 'Great Mortar', 'Yayatustenuggee', 'Opothleyaholo ', 'William Weatherford', 'Lamochattee', 'William McIntosh', 'McGillivray', ],
        'Osage Indians': ['Fred Lookout', 'Charles Tillman', 'John Red Eagle', 'Little Osage', 'James Bigheart', 'Shonka Sabe', 'John Joseph Mathews',  'Tink Tinker', 'Chief White Hair', 'Maria Tallchief', 'Marjorie Tallchief', 'Arthur Bonnicastle', 'Paul Red Eagle', 'Sylvester Tinker', 'Charles O. Tillman', 'Scott Bighorse', 'Standing Bear', 'Henry Red Eagle', 'Chief Red Eagle', 'Geoffrey M. Standing Bear'],
        'Comanche Indians': ['Quanah Parker', 'Wallace Coffey', 'Shoshoni', 'Shoshone', 'Charles Chibitty', 'Peta Nocona', 'White Parker', 'Jesse Ed Davis', 'ten bears', 'Chief White Eagle', 'Buffalo Hump', 'Iron Jacket', 'Yellow Wolf', 'Woommavovah'],
        'Kiowa Indians': ['Clyde Mithlo', 'Phillip Jack Anquoe', 'Billy Evans Horse', 'J.T. Goombi', 'JT Goombi', 'Sitting Bear', 'Guipago', 'Satanta', 'Chief Lone Wolf', 'Ahpeahtone', 'Horace Poolaw', 'Pascal Poolaw', 'Jack Hokeah', 'Spencer Asah', 'James Auchiah', 'Chief Big Bow', 'Lawrence SpottedBird'],
        'Pawnee Indians': ['Andrew Knife Chief', 'Walter Echo-Hawk', 'Albert Gourd', 'Sun Chief', 'Sharitahrish', 'Big Spotted Horse', 'John EchoHawk', 'Larry Echo Hawk', 'Petalesharo', 'Wicked Chief', 'Ralph Haymond', 'Warren Pratt', 'Lester Moon Eagle', 'Morgan Littel Sun', 'Pat Leading Fox', 'Chief Little Sun', 'Chief Horsechief', 'Spotted Horsechief', 'Gilbert Beard', 'Misty Nuttle', 'Misty M. Nuttle'],
        'Sac and Fox Indians': ['George Thurman', 'Jim Thorpe', 'Thakiwaki', 'Chief Appanoose', 'Keokuk', 'Mokohoko', 'Don Abney', 'Don W. Abney', 'Dora Ortega', 'Dora S. Ortega', 'Schexnider', 'Peggy Acoya', 'Mary F. McCormick', 'Mary McCormick'],
        'Shawnee Indians': ['Chief Big Jim', 'Chief Black Bob', 'Chief Bluejacket', 'Chief Catahecassa', 'Chief Paxinos', 'Tenskwatawa', 'Chief Tecumseh', 'Chief Nererahhe'],
        'Ponca Indians': ['Chief White Eagle', 'Clyde Warrior', 'Chief Standing Bear', 'Carter Camp'],
        'Cheyenne-Arapaho': ['William "Hawk" Birdshead', 'Suzan Shown Harjo', 'Viola Hatch', 'Yvonne Kauger', 'Chief Little Raven', 'Henrietta Mann', 'Chief Niwot', 'St. David Pendleton Oakerhater', 'Harvey Pratt', 'Henry Roman Nose', 'W. Richard West', 'Gilbert Miles'],
        'Kaw Indians': ['Lucy Tayiah Eads', 'Washunga', 'White Plume', 'Mochousia', 'Jim Pepper', 'Walter Kekahbah', 'Allegawaho', 'KnoShr'], 
        'Caddo Indians': ['Dehahuit', 'Bobby Gonzalez'],
        'Iowa Indians': ['Chief Mahaska', 'Big Neck', 'Moanahonga', 'Mary Louise White Cloud', 'Jacob Keyes']
    }

    leader_to_tribe_mapping = {leader: tribe for tribe, leaders in tribal_leaders_mapping.items() for leader in leaders}

    # Define case categories
    tribal_sovereignty_cases = {'Cherokee Nation v. Georgia', 'Worcester v. Georgia', 'United States v. Kagama', 'Oklahoma Tax Commission v. United States', 'Menominee Tribe v. United States', 'Morton v. Mancari', 'Bryan v. Itasca County', 'Oliphant v. Suquamish Indian Tribe', 'United States v. Wheeler', 'Santa Clara Pueblo v. Martinez', 'Washington v. Confederated Bands and Tribes of the Yakima Indian Nation', 'Washington v. Confederated Tribes of Colville Reservation', 'White Mountain Apache Tribe v. Bracker', 'Merrion v. Jicarilla Apache Tribe', 'Ramah Navajo School Bd., Inc. v. Bureau of Revenue of N.M.', 'New Mexico v. Mescalero Apache Tribe', 'National Farmers Union Ins. Cos. v. Crow Tribe', 'Three Affiliated Tribes of Fort Berthold Reservation v. Wold Engineering, P. C.', 'Cotton Petroleum Corp. v. New Mexico', 'Brendale v. Confederated Yakima Indian Nation', 'Duro v. Reina', 'Oklahoma Tax Commission v. Citizen Band of Potawatomi Tribe of Okla.', 'Yakima v. Confederated Tribes', 'Dept. of Taxation and Finance of N.Y. v. Milhelm Attea & Bros., Inc.', 'United States v. Lara', 'Wagnon v. Prairie Band Potawatomi Indians', 'Plains Commerce Bank v. Long Family Land and Cattle Co., Inc.'}
    allotment_cases = {'Arenas v. United States', 'Brendale v. Confederated Yakima Indian Nation', 'Yakima v. Confederated Tribes', 'Plains Commerce Bank v. Long Family Land and Cattle Co.', 'United States v. Mitchell'}
    property_rights_cases = {'Oklahoma Tax Commission v. United States', 'United States v. Southern Ute Tribe or Band of Indians', 'United States v. Sioux Nation of Indians', 'Rice v. Rehner', 'Brendale v. Confederated Yakima Indian Nation', 'Oklahoma Tax Commission v. Citizen Band of Potawatomi Tribe of Okla.', 'Yakima v. Confederated Tribes', 'South Dakota v. Bourland', 'Plains Commerce Bank v. Long Family Land and Cattle Co.'}
    tribal_reservations_cases = {'United States v. Southern Ute Tribe or Band of Indians', 'McClanahan v. Arizona State Tax Commission', 'Oliphant v. Suquamish Indian Tribe', 'Washington v. Confederated Bands and Tribes of the Yakima Indian Nation', 'Washington v. Confederated Tribes of Colville Reservation', 'White Mountain Apache Tribe v. Bracker', 'United States v. Sioux Nation of Indians', 'Merrion v. Jicarilla Apache Tribe', 'New Mexico v. Mescalero Apache Tribe', 'Rice v. Rehner', 'Oregon Dept. of Fish and Wildlife v. Klamath Indian Tribe', 'California v. Cabazon Band of Mission Indians', 'Mississippi Band of Choctaw Indians v. Holyfield', 'Brendale v. Confederated Yakima Indian Nation', 'Oklahoma Tax Commission v. Citizen Band of Potawatomi Tribe of Okla.', 'South Dakota v. Bourland', 'Plains Commerce Bank v. Long Family Land and Cattle Co.'}
    tribal_citizenship_cases = {'Ex parte Joins', 'Santa Clara Pueblo v. Martinez', 'Mississippi Band of Choctaw Indians v. Holyfield', 'South Dakota v. Bourland'}
    taxation_cases = {'Oklahoma Tax Commission v. United States', 'Mescalero Apache Tribe v. Jones', 'McClanahan v. Arizona State Tax Commission', 'Bryan v. Itasca County', 'Washington v. Confederated Tribes of Colville Reservation', 'White Mountain Apache Tribe v. Bracker', 'Ramah Navajo School Bd., Inc. v. Bureau of Revenue of N.M.', 'New Mexico v. Mescalero Apache Tribe', 'Cotton Petroleum Corp. v. New Mexico', 'Oklahoma Tax Commission v. Citizen Band of Potawatomi Tribe of Okla.', 'Yakima v. Confederated Tribes', 'Oklahoma Tax Commission v. Sac & Fox Nation', 'Dept. of Taxation and Finance of N.Y. v. Milhelm Attea & Bros., Inc.', 'Wagnon v. Prairie Band Potawatomi Indians'}
    american_indian_claims = {'Alaska Native Allotment Act', 'Alaska Native Claims Settlement Act', 'American Indian Religious Freedom Act', 'American Indian Trust Fund Management Reform Act', 'Burke Act', 'Cherokee Nation vs. Georgia', 'Civilization Fund Act', 'Clean Air Act', 'Clean Water Act', 'Creek Nation V. United States', 'Curtis Act', 'Dawes Act', 'Forced Relocation', 'Hawaiian Homelands', 'House concurrent resolution 108', 'Indian Arts and Crafts Act', 'Indian Census Act', 'Indian Child Welfare Act', 'Indian Citizenship Act', 'Indian Civil Rights Act', 'Indian Claims Commission Act', 'Indian Claims Limitations Act', 'Indian Gaming Regulatory Act', 'Indian Homesteading', 'Indian Intercourse Act', 'Indian Land Consolidation Act', 'Indian Relocation Act', 'Indian Removal Act', 'Indian Reorganization Act', 'Indian Self-Determination And Education Assistance Act', 'Indian Vaccination Act', 'Johnson–OMalley Act', 'Lacey Act', 'Major Crimes Act', 'McGirt v. Oklahoma', 'Menominee Restoration Act', 'Meriam Report', 'Mission Indian Act', 'Native American Graves Protection and Repatriation Act', 'Native American Housing Assistance and Self-Determination Act', 'Native American Languages Act', 'Nelson Act', 'Oklahoma Enabling Act', 'Oklahoma Indian Welfare Act', 'Public Law 280', 'Reconstruction Act', 'Repatriation Act', 'Standing Rock Reservation', 'Tee-Hit-Ton Indians', 'Termination Act', 'Thomas-Rogers Act', 'Title 25', 'Tribal Law and Order Act', 'Tribal Self-Governance Amendments', 'Western Shoshone Claims Distribution Act', 'White Mountain Apache Tribe Water Rights Quantification Act'}

    # Function to preprocess text
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r'[^A-Za-z0-9\s]', '', text)
        return text

    # Function to post-process text
    def postprocess_text(text):
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # Function to categorize legal cases
    def categorize_legal_cases(text):
        categorized_cases = {
            'Tribal Sovereignty Cases': [],
            'Allotment Cases': [],
            'Property Rights Cases': [],
            'Tribal Reservations Cases': [],
            'Tribal Citizenship Cases': [],
            'Taxation Cases': [],
            'American Indian Claims': [],
        }

        for case in tribal_sovereignty_cases:
            if case.lower() in text.lower():
                categorized_cases['Tribal Sovereignty Cases'].append(case)
                
        for case in allotment_cases:
            if case.lower() in text.lower():
                categorized_cases['Allotment Cases'].append(case)
                
        for case in property_rights_cases:
            if case.lower() in text.lower():
                categorized_cases['Property Rights Cases'].append(case)
                
        for case in tribal_reservations_cases:
            if case.lower() in text.lower():
                categorized_cases['Tribal Reservations Cases'].append(case)

        for case in tribal_citizenship_cases:
            if case.lower() in text.lower():
                categorized_cases['Tribal Citizenship Cases'].append(case)

        for case in taxation_cases:
            if case.lower() in text.lower():
                categorized_cases['Taxation Cases'].append(case)

        for case in american_indian_claims:
            if case.lower() in text.lower():
                categorized_cases['American Indian Claims'].append(case)

        return categorized_cases
        
    # Function to generate title using ChatGPT
    def generate_title(text, max_retries=5, retry_delay=5):
        """
        Generates a title using OpenAI API with retry logic and rate limiting.
        """
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Create a title for the following text:\n{text}"}],
                    max_tokens=35,
                    n=1,
                    temperature=0.7
                )
                return response['choices'][0]['message']['content'].strip()

            except openai.error.RateLimitError as e:
                print(f"Rate limit hit. Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

            except Exception as e:
                print(f"API request failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise e  # If max retries are exhausted, raise the exception

        return None

    # Function to generate summary using ChatGPT
    def generate_summary(text, max_summary_length=200):
        for attempt in range(MAX_RETRIES):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Summarize the following text:\n{text}\nSummary:"}],
                    max_tokens=max_summary_length,
                    n=1,
                    temperature=0.7
                )
                return response['choices'][0]['message']['content'].strip()
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"API request failed, retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

    # Function to analyze summary for creators and recipients
    def analyze_summary(summary):
        doc = nlp(summary)
        creator, recipient = None, None

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                prev_token = doc[ent.start - 1].lower_ if ent.start > 0 else ''
                next_token = doc[ent.end].lower_ if ent.end < len(doc) else ''
                if prev_token in ["from", "by", "mr.", "mrs.", "ms.", "dr."] or next_token in ["writes", "wrote"]:
                    creator = ent.text
                elif prev_token in ["to", "urging"] or "response" in ent.sent.text.lower():
                    recipient = ent.text

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
    # Function to assign subjects to transcripts
    def assign_subjects(transcript, max_subjects=3):
        keyword_subject_mapping = {
            'Abortion--Law and legislation--United States': [
                'pro-choice', 'pro-life', 'reproductive rights', 'family planning',
                'roe v. wade', 'planned parenthood', 'heartbeat bill', 'abortion', 'sex education'
            ],
            'Advertising, Political--United States': [
                'campaign advertisement', 'campaign commercial', 'political media', 'propaganda',
                'political campaign communication', 'advertising', 'television ad', 'radio ad', 
                'associated press', 'press corp'
            ],
            'Aeronautics': [
                'aviation', 'federal aviation administration', 'air traffic control', 'aerospace',
                'airplane pilot', 'Airport Improvement Program', 'National Airspace System', 
                'Unmanned Aircraft Systems', 'airspace', 'Transportation Security Administration', 
                'air travel', 'skylab'
            ],
            'Aerospace engineering': [
                'rocket science', 'satellite design', 'spacecraft engineering', 'aerodynamics', 'jet propulsion'
            ],
            'African Americans': [
                'black american', 'afro-american', 'colored man', 'civil rights', 'black community', 
                'colored woman', 'black man', 'black woman', 'negro'
            ],
            'Age Discrimination': [
                'retirement age', 'age discrimination', 'ageism', 'early retirement', 'elderly discrimination', 
                'mandatory retirement', 'employment equality', 'older workers benefit protection act'
            ],
            'Age discrimination in employment': [
                'older workers', 'workforce equality', 'retirement age', 'age discrimination in workplace'
            ],
            'Aging -- Social aspects': [
                'elder care', 'aging population', 'senior citizen', 'retirement communities', 'gerontology'
            ],
            'Agricultural laws and legislation--United States': [
                'farming regulations', 'usda', 'farm bill', 'crop subsidies', 'food safety', 
                'agriculture and food act', 'national agricultural bargaining board', 'tobacco import', 
                'tobacco export', 'agricultural trade development', 'farm', 'farms', 'farmers', 'organic farm', 
                'food and drug administration', 'coffee export', 'organic farming', 'agricultural food act', 
                'mexican produce'
            ],
            'Agricultural policy--United States': [
                'farmers', 'rural development', 'food production', 'agribusiness'
            ],
            'Agricultural subsidies--United States': [
                'crop pricing', 'farm subsidies', 'market demand', 'farm credit', 'agricultural disaster relief', 
                'farm loan and credit issues', 'crop insurance programs', 'federal milk supply', 'wheat programs', 
                'agricultural adjustment act', 'wool act', 'sugar act'
            ],
            'Ambassadors--United States': [
                'foreign relations', 'embassy', 'consulates', 'international relations', 'ambassador'
            ],
            'Armed conflict': [
                'war', 'military engagement', 'combat', 'conflict zones'
            ],
            'Armed Forces--United States': [
                'us military', 'army', 'navy', 'marines', 'air force', 'artillery'
            ],
            'Arms Control': [
                'disarmament', 'nuclear weapons', 'chemical weapons', 'biological weapons', 
                'strategic arms limitation talk', 'strategic arms reduction treaty', 
                'intermediate-range nuclear forces treaty', 'chemical weapons convention', 
                'missile technology control regime', 'arms race', 'cuban missile crisis', 'ballistic missile'
            ],
            'Astronautics': [
                'space exploration', 'space shuttle', 'space capsule', 'moon landing', 'challenger space', 
                'National Aeronautics and Space Administration', 'skylab', 'lunar gateway', 'space program', 
                'National Advisory Committee for Aeronautics', 'NASA'
            ],
            'Atomic bomb': [
                'nuclear weapon', 'atomic energy', 'hiroshima', 'manhattan project', 'nuclear warfare'
            ],
            'Banking law': [
                'financial regulation', 'bank compliance', 'federal reserve', 'securities act', 'financial institution'
            ],
            'Banking reform': [
                'dodd-frank', 'financial regulation', 'banking oversight', 'bank bailout', 'fdic'
            ],
            'Bankruptcy': [
                'chapter 11', 'debt relief', 'bankruptcy court', 'restructuring', 'chapter 13', 'municipal bankruptcy', 
                'bankruptcy code'
            ],
            'Banks and banking--United States': [
                'finance', 'federal reserve', 'department of commerce', 'national bureau of standards', 
                'federal regulation', 'interstate commerce act', 'federal deposit insurance corporation', 
                'resolution trust corporation', 'savings and loan crisis', 'federal savings and loan insurance', 
                'insolvent savings and loan association', 'federal credit union act', 'bank holding company act', 
                'truth in lending act', 'federal reserve board', 'securities exchange commission', 'commodity futures', 
                'securities exchange act', 'public utility holding company act', 'credit control act'
            ],
            'Biography--Political aspects': [
                'memoirs', 'political history', 'personal narratives', 'political biographies', 'life stories', 
                'memoir', 'biography', 'obituary'
            ],
            'Budget--United States': [
                'federal budget', 'government spending', 'deficit', 'budget cut'
            ],
            'Business--United States': [
                'commerce', 'corporations', 'entrepreneurship', 'small business', 'supply chain'
            ],
            'Campaign management--United States': [
                'campaign donations', 'campaign fund', 'campaign fundraising', 'political action committee', 
                'Federal Election Commission', 'Center for Responsive Politics', 'consumer watchdog', 'elections', 
                'voters', 'voting rights', 'campaign finance', 'campaign advertisement', 'candidate debate'
            ],
            'Capital punishment': [
                'death penalty', 'execution', 'lethal injection', 'criminal justice', 'life sentence', 'electric chair', 
                'death sentence'
            ],
            'Child health services': [
                'pediatric care', 'childhood vaccination', 'school health service', 'health screening', 
                'nutrition program', 'youth health', 'infant care', 'infant health'
            ],
            'Civil rights and socialism': [
                'civil liberties', 'socialist movements', 'equal rights', 'freedom', 'socialism', 'social equity', 
                'communal economics', 'cooperative economy', 'collective welfare', 'civil liberty'
            ],
            'Civil rights--United States': [
                'civil rights', 'civil liberties', 'equal protection', 'fair housing initiatives', 'voting rights', 
                'right to vote', 'human rights', 'equal rights', 'equal opportunity', 'gay rights', '13th amendment', 
                '14th amendment', 'black code', 'social justice', '15th amendment'
            ],
            'Civil rights--United States--Cases': [
                'landmark case', 'court rulings', 'civil rights litigation', 'brown v. board', 'civil rights act', 
                'civil liberties', 'discrimination lawsuit', 'equal protection clause', 'segregation', 
                'voting rights act', 'affirmative action', 'freedom of speech', 'title IX', 'loving v. virginia', 
                'desegregation', 'mclaurin v. oklahoma', 'sipuel v. board', 'mcgirt', 'voter suppression', 
                'tulsa race riot', 'greenwood race'
            ],
            'Civil rights--United States--History': [
                'civil rights movement', 'segregation', 'jim crow', 'martin luther king', 'civil rights era', 'sit-ins', 
                'native american rights', 'american indian movement', 'clara luper', 'equal rights amendment', 
                'women’s rights', 'wilma mankiller', 'ladonna harris'
            ],
            'Civil Defense': [
                'civil reserve air fleet', 'federal civil defense act', 'nuclear warfare', 
                'civil defense air raid shelter program', 'civil air patrol', 'domestic terrorism prevention', 
                'air raid siren', 'fallout shelter'
            ],
            'Civil service--United States': [
                'government jobs', 'public sector', 'federal employment', 'civil servants'
            ],
            'Climatology--United States': [
                'weather pattern', 'climate change', 'meteorology', 'environmental science', 'global warming', 'weather'
            ],
            'Commerce': [
                'international trade', 'commerce regulation', 'economic policy'
            ],
            'Communication--Political aspects': [
                'political media', 'public communication', 'political speeches', 'political messaging', 'propaganda', 
                'political speech', 'congressional speech', 'presidential speech'
            ],
            'Community health services--United States': [
                'public health', 'community clinics', 'affordable care', 'disease prevention', 'mental health services', 
                'indian health service', 'tribal health', 'substance abuse treatment', 'vaccination', 
                'federal health assistance', 'health equity', 'community outreach'
            ],
            'Community mental health services': [
                'mental health clinic', 'outpatient service', 'counseling', 'psychiatric care', 'therapy', 
                'behavioral health', 'recovery program', 'suicide prevention'
            ],
            'Constituents\' communication with members of the U.S. Congress': [
                'letter to congress', 'constituent service', 'public opinion', 'petition', 'letter to', 
                'letter from', 'received from', 'constituent correspondence'
            ],
            'Correspondence files--Management--Congresses': [
                'file management', 'records retention', 'document archiving', 'government correspondence'
            ],
            'Courts--United States': [
                'supreme court', 'judiciary', 'federal court', 'court ruling', 'legal system', 'legal case'
            ],
            'Crime--United States': [
                'criminal offense', 'law enforcement', 'criminal justice', 'domestic violence', 'murder', 
                'larceny', 'federal bureau of investigation', 'FBI', 'penal code', 'crime rate', 'recidivism', 
                'forensic', 'dna evidence', 'violent crime'
            ],
            'Cultural assimilation--United States--History': [
                'melting pot', 'immigrant integration', 'americanization', 'multiculturalism', 'assimilation policies'
            ],
            'Cultural heritage--Protection--United States': [
                'heritage conservation', 'historic preservation', 'cultural site', 'national monument', 'museum collection'
            ],
            'Cultural property--Protection--United States': [
                'artifact preservation', 'intangible heritage', 'cultural site', 'heritage law', 'patrimony'
            ],
            'Death penalty': [
                'capital punishment', 'legal justice', 'criminal punishment', 'death row'
            ],
            'Death row inmates': [
                'capital offenders', 'prisoners', 'death penalty', 'criminal justice'
            ],
            'Economic Development--United States': [
                'economic growth', 'infrastructure project', 'business development', 'job creation', 'urban renewal'
            ],
            'Economics and Public Finance': [
                'public expenditure', 'macroeconomics', 'fiscal policy', 'government debt'
            ],
            'Educational policy--United States': [
                'education reform', 'school funding', 'curriculum standards', 'teacher evaluation', 'student performance', 
                'standardized testing', 'Brown v. Board', 'Common Core Standards', 'Desegregation policy', 
                'Higher Education Act'
            ],
            'Education--United States': [
                'school', 'universities', 'k-12 education', 'college admissions', 'vocational education', 
                'illiteracy', 'literacy', 'university', 'education', 'trade school', 'charter school', 
                'higher education', 'student loan'
            ],
            'Election laws': [
                'voting regulation', 'election procedure', 'campaign finance law', 'voter ID law', 'gerrymandering'
            ],
            'Electric power production': [
                'tennessee valley authority', 'bonneville power administration', 'electric power plant', 
                'hydroelectric power', 'utility payment reform', 'federal energy regulatory commission', 'ferc', 
                'rural electrification', 'electric cooperative', 'electric utility rate reform', 'smart grid', 
                'power plant', 'electric utilities', 'power supply', 'federal power commission', 'atomic energy', 
                'hydroelectric', 'public utilities', 'coal-fired power', 'high voltage'
            ],
            'Emergency Management': [
                'disaster response', 'fema', 'crisis management', 'emergency services', 'evacuations', 
                'emergency management', 'disaster planning', 'early warning system', 'flood insurance', 
                'disaster mitigation'
            ],
            'Employee fringe benefits': [
                'health insurance', 'pension plan', 'retirement benefit', 'sick leave', 'vacation days', 
                'unemployment compensation', 'employee benefits'
            ],
            'Employment & social affairs': [
                'labor market', 'job opportunities', 'workplace policy', 'unemployment', 'social welfare'
            ],
            'Endangered species': [
                'wildlife conservation', 'habitat protection', 'species preservation', 'environmental law', 
                'animal protection', 'environmental protection', 'animal welfare', 'animal rights'
            ],
            'Energy policy--United States': [
                'renewable energy', 'oil and gas', 'nuclear power', 'energy conservation', 'electric grid', 'wind power', 
                'solar power', 'nuclear regulatory', 'alternative fuel', 'energy advisory', 'fossil fuel', 
                'power supply', 'power grid'
            ],
            'Environmental Protection': [
                'drain water', 'dust control', 'environmental protection agency', 'council on environmental quality', 
                'energy research and development association', 'erda', 'clean air', 'national environmental policy act', 
                'epa regulations', 'pollution control', 'natural resources', 'clean water', 'toxic substance', 'air quality'
            ],
            'Farm legislation--United States': [
                'farm bill', 'agricultural subsidies', 'crop insurance', 'farming regulations', 'usda'
            ],
            'Federal Indian policy--Education': [
                'tribal education', 'indian schools', 'native american students', 'federal assistance', 'indian affairs'
            ],
            'Flood control--United States': [
                'levees', 'dams', 'water management', 'flood insurance', 'disaster mitigation', 'erosion', 
                'watershed', 'flood control'
            ],
            'Food--Safety measures': [
                'animal drug residues', 'consumer seafood safety', 'food labeling requirements', 'grain inspection services', 
                'pesticide residues on fruit', 'food irradiation control act', 'meat grading standards'
            ],
            'Foreign trade regulation--Congresses': [
                'tariffs', 'trade barriers', 'world trade organization'
            ],
            'Foreign relations': [
                'international war', 'world war', 'global politics', 'allies', 'peace corps', 'foreign assistance act'
            ],
            'Freedom of speech -- United States': [
                'freedom of speech', 'freedom of assembly', 'freedom of religion', 'freedom of the press', 
                'school prayer', 'censorship', 'free press', 'protest speech', 'protest', 'banned books', 
                'dennis v. united states', 'tinker v. des moines', 'texas v. johnson'
            ],
            'Gender identity--Social aspects': [
                'gay', 'homosexual', 'sexual identity', 'sexual orientation', 'social security inequities', 
                'female salary inequities', 'same sex marriage', 'transgender rights', 'transgender', 'lgbt'
            ],
            'Geriatric health services': [
                'elderly care', 'nursing home', 'geriatric medicine', 'senior health', 'assisted living'
            ],
            'Government correspondence': [
                'official communication', 'government documents', 'email archives', 'public records', 'Diplomatic cables'
            ],
            'Gun Control': [
                'Automatic weapon', 'Semiautomatic weapon', 'second amendment', 'national rifle association', 
                'gun safety', 'Gun Control Act', 'Assault weapon'
            ],
            'Health': [
                'public health', 'wellness', 'disease prevention', 'mental health', 'healthcare systems'
            ],
            'Health care for the aging': [
                'medicare', 'elder care', 'geriatrics', 'home healthcare', 'retirement communities'
            ],
            'Health Care for the Homeless Program (U.S.)': [
                'homeless healthcare', 'medical outreach', 'social services', 'community health clinics'
            ],
            'Health education': [
                'public health campaign', 'school health program', 'sex education', 'nutrition education', 'disease prevention'
            ],
            'Health insurance--Law and legislation--United States': [
                'optometry', 'dental insurance', 'cancer treatment', 'medicare', 'medicaid', 'insurance premium'
            ],
            'Higher education--United States': [
                'universities', 'college', 'graduate programs', 'student loans', 'college admissions'
            ],
            'Homelessness': [
                'homeless shelter', 'housing insecurity', 'public assistance', 'poverty'
            ],
            'Housing--Law and legislation': [
                'section 8', 'housing authority', 'home owners association', 'city council'
            ],
            'Humanities': [
                'cultural studies', 'social sciences', 'national endowment for the humanities'
            ],
            'Immigrants--Legal status, laws, etc.': [
                'immigrant', 'political asylum', 'immigration', 'migrant work', 'naturalization', 'border control', 
                'asylum', 'refugee', 'border patrol'
            ],
            'Income tax': [
                'tax bracket', 'tax return', 'irs', 'income tax credit', 'federal income tax'
            ],
            'Indians of North America--Civil rights': [
                'tribal sovereignty', 'native american rights', 'land claim', 'self-determination', 'tribal governance'
            ],
            'Indians of North America--Claims': [
                'land rights', 'treaties', 'land dispute', 'Indian Claims Commission', 'tribal sovereignty'
            ],
            'Indians of North America--Health': [
                'indian health service', 'tribal healthcare', 'public health', 'native american health'
            ],
            'Indians of North American--Education': [
                'tribal education', 'native american schools', 'federal indian education', 'tribal colleges'
            ],
            'Indians of North America--Oklahoma': [
                'tribe', 'tribal', 'american indian', 'native american', 'principal chief'
            ],
            'Indians of North America--Politics and government': [
                'tribal council', 'tribal sovereignty', 'self-governance', 'bureau of indian affairs', 'tribal court'
            ],
            'Indians of North America--Religion': [
                'native spirituality', 'sacred site', 'oral tradition', 'spiritual practices', 'sun dance'
            ],
            'Indians of North America--Sovereignty': [
                'self-governance', 'tribal sovereignty', 'federal recognition', 'land claim', 'treaty rights'
            ],
            'Indians of North America--Treaties': [
                'treaty rights', 'land cessions', 'federal recognition', 'tribal agreements', 'treaty violations'
            ],
            'Indians of North America--Tribal citizenship': [
                'tribal enrollment', 'blood quantum', 'citizenship requirements', 'tribal rolls', 'federal recognition'
            ],
            'Indians of North America--United States': [
                'native americans', 'tribal nations', 'treaty rights', 'self-determination'
            ],
            'Inflation (Finance)': [
                'price increases', 'cost of living', 'economic policy', 'interest rates', 'federal reserve'
            ],
            'Labor laws and legislation': [
                'employment law', 'minimum wage', 'labor unions', 'workers rights', 'overtime pay'
            ],
            'Labor movement--United States': [
                'union organizing', 'collective bargaining', 'labor strike', 'workers rights', 'labor union'
            ],
            'Labor Unions--United States': [
                'afl-cio', 'teamster', 'service employees international union', 'labor movement', 'workers rights'
            ],
            'Land use--Law and legislation--United States': [
                'zoning law', 'property rights', 'eminent domain', 'urban planning', 'development'
            ],
            'Land use--Planning': [
                'zoning', 'development', 'city boundaries', 'museum', 'public park'
            ],
            'Mental health services': [
                'mental health clinics', 'community services', 'counseling', 'therapy', 'psychiatric care'
            ],
            'Meteorology--United States': [
                'weather patterns', 'climate science', 'atmospheric research', 'storm tracking', 'weather forecasting'
            ],
            'Military education--Law and legislation': [
                'rotc', 'reserve officers training corps', 'west point', 'the citadel', 'GI bill'
            ],
            'Military reserves--United States': [
                'national guard', 'army reserves', 'navy reserve', 'military readiness', 'air force reserve'
            ],
            'Military weapons': [
                'artillery', 'ballistic missiles', 'tanks', 'military equipment', 'fighter jet', 'chemical weapon'
            ],
            'Minimum wage': [
                'wage law', 'living wage', 'income inequality', 'federal minimum wage', 'wage increase'
            ],
            'Monetary policy--United States': [
                'federal reserve', 'interest rates', 'economic growth', 'inflation control', 'macroeconomics'
            ],
            'Nuclear warfare': [
                'atomic bomb', 'deterrence', 'nuclear arms race', 'cold war', 'mutual assured destruction'
            ],
            'Older people—Health and hygiene': [
                'elder care', 'geriatric medicine', 'aging population', 'senior health', 'nursing homes'
            ],
            'People with disabilities—Civil rights': [
                'accessibility rights', 'disability', 'americans with disabilities', 'social security disability'
            ],
            'Political campaigns--United States': [
                'election campaign', 'campaign finance', 'political ad', 'voter outreach', 'political strategy'
            ],
            'Political corruption': [
                'bribery', 'fraud', 'scandal', 'abuse of power', 'political malfeasance', 'watergate'
            ],
            'Property tax': [
                'real estate tax', 'property assessment', 'tax reform', 'local tax', 'homeownership'
            ],
            'Public health--United States': [
                'healthcare access', 'vaccination programs', 'disease prevention', 'public health campaigns'
            ],
            'Public housing': [
                'affordable housing', 'section 8', 'subsidized housing', 'housing policy', 'urban development'
            ],
            'Race discrimination': [
                'ku klux klan', 'desegregation', 'race based crime', 'racial wealth gap', 'racial profiling'
            ],
            'Retirement': [
                'social security', 'pension plans', '401k', 'retirement age', 'elder care', 'medicare'
            ],
            'Sales tax--United States': [
                'tax policy', 'sales tax', 'consumer tax', 'tax reform', 'state tax'
            ],
            'Science': [
                'scientific research', 'technology', 'natural sciences', 'innovation'
            ],
            'Space exploration': [
                'nasa', 'astronomy', 'space travel', 'satellite mission', 'human spaceflight'
            ],
            'Tax fraud': [
                'tax evasion', 'illegal deductions', 'tax shelter', 'financial crime', 'irs investigation'
            ],
            'Voting rights': [
                'suffrage', 'voter protection', 'voting law', 'voter disenfranchisement']
                
        }

        assigned_subjects = []
        transcript_lower = transcript.lower()
        subject_keyword_matches = defaultdict(int)

        for subject, keywords in keyword_subject_mapping.items():
            for keyword in keywords:
                stemmed_keyword = stemmer.stem(keyword.lower())
                if stemmed_keyword in transcript_lower:
                    subject_keyword_matches[subject] += transcript_lower.count(stemmed_keyword)

        for subject, _ in sorted(subject_keyword_matches.items(), key=lambda item: item[1], reverse=True)[:max_subjects]:
            assigned_subjects.append(subject)

        return assigned_subjects

    # Function to extract tribes from text
    def extract_tribes(text):
        text_lower = text.lower()
        extracted_tribes = [tribe for tribe in predefined_tribes if tribe.lower() in text_lower]
        return extracted_tribes

    # Function to extract tribal organizations from tribes
    def extract_tribal_organizations(extracted_tribes):
        tribal_organizations = [tribal_leaders_mapping.get(tribe, []) for tribe in extracted_tribes]
        return list(set(sum(tribal_organizations, [])))

    # Function to find and tag tribal leaders
    def find_and_tag_tribal_leaders(text):
        found_leaders_with_tribes = [(leader, tribe) for leader, tribe in leader_to_tribe_mapping.items() if leader.lower() in text.lower()]
        return found_leaders_with_tribes

    # Function to extract dates from text
    def extract_dates(text):
        date_pattern = r'(\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2}, \d{4}|\b(?:19[89][7-9]|20[01][0-9])\b))'
        return list(set(re.findall(date_pattern, text)))

    # Function to extract named entities from text
    def extract_named_entities(text):
        doc = nlp(text)
        return [ent.text for ent in doc.ents]

    # Function to extract states from text
    def extract_states(text):
        doc = nlp(text)
        recognized_states = {ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]}
        recognized_countries = {"United States", "Canada", "Mexico"}
        return [state for state in recognized_states if state not in recognized_countries]

    # Function to assign policies from list
    def assign_policy(summary, text):
        predefined_policies = {
            'Agriculture and Food': ['US Department of Agriculture ', 'USDA', 'Food and Drug Administration'], 
            'Animals': ['endangered species', 'animal welfare', 'marine protection', 'animal cargo', 'Exotic Wildlife', 'Animal Abuse', 'Animal Rights'], 
            'Armed Forces and National Security': [ 'national security', 'homeland security', 'department of homeland security', 'air patrol', 'civil defense'], 
            'Arts, Culture, Religion': ['Archaeological', 'Archaeology', 'national endowment for the humanities ', 'libraries', 'museum exhibit', 'cultural center', 'sound recording', 'motion picture',  'cultural property', 'cultural resource', 'cultural relations', 'religious freedom', 'separation of church and state'], 
            'Civil Rights and Liberties, Minority Issues': ['First Amendment', 'civil rights', 'civil disobedience', 'due process', 'abortion rights', 'minority health', 'equal rights', 'segregation', 'civil liberties', 'equal protection',  'fair housing',  'Indian Bill of Rights',  'National Indian Youth Council',  'cruel and unusual punishment', 'tribal sovereignty', 'National Indian Education Association ', 'American Indian Religious Freedom Act', 'Indian Appropriations', 'Indian Gaming Regulatory Act', 'Marshall Trilogy', 'fourteenth amendment ', '14th amendment', 'treaty of fort laramie', 'Oklahoma Enabling Act', 'Indian Citizenship Act', 'Nationality Act', 'domestic dependent nations', 'cultural assimilation', 'colonization', 'freedom of speech', 'peyote',  'equal education', 'Indian schools', 'Bureau of Indian Affairs ', 'voting rights', 'voting age'], 
            'Commerce': ['business law', 'business loans', 'small business', 'consumer protection', 'manufacturing',  'consumer affairs', 'trade practices', 'intellectual property', 'imports and exports', 'foreign trade', 'finance policy', 'tariff', 'monopoly'], 
            'Congress': ['congressional committee', 'congressional oversight',  'Legislative Lobbying', 'Policy Reform', 'Policy Amendment', 'Congressional Act', 'Acts of Congress', 'Legislative Measure','Congressional Sponsor'], 
            'Crime and Law Enforcement': ['criminal offenses', 'law enforcement',  'domestic violence', 'conviction', 'Federal Bureau of Investigation ', 'FBI', 'penal code', 'crime rate', 'recidivism', 'drug policy', 'criminal justice', 'juvenile court', 'gun control', 'witness protection', 'criminal justice oversight', 'sentencing reform', 'crime prevention'], 
            'Economics and Public Finance': ['budget appropriation', 'public debt', 'government lending', 'government account', 'monetary policy', 'economic theory', 'fiscal policy', 'tax reform', 'balanced budget', 'budget deficit', 'inflation', 'housing finance', 'gross domestic product', 'economic development', 'government bailout', 'central bank', 'global supply chain', 'free market'], 
            'Education': ['sequoyah system', 'global alphabet', 'Job Training Partnership Act',  'educational reform', 'federal elementary and secondary education program', 'Safe Schools Act', 'Department of Education', 'literacy', 'illiteracy', 'rural education initiative', 'Native American Education Act', 'Bureau of Indian Education', 'Tribal colleges and universities', 'Indian Education Act', 'Indian Education Policy Review', 'Native American Languages Act', 'Indian Self-Determination and Education Assistance Act', 'tribal education', 'Johnson-OMalley Act', 'Indian School Equalization Program', 'education disparities', 'Indigenous curriculum', 'language preservation', 'tribal schools', 'ICWA', 'Indian Child Welfare Act '], 
            'Emergency Management': ['Federal Emergency Management Agency', 'FEMA', 'disaster planning', 'early warning system', 'drought relief', 'National Fire Academy', 'flood insurance', 'earthquake', 'disaster mitigation', 'disaster preparedness', 'Tribal Homeland Security Grant Program', 'Tribal Emergency Operations Centers', 'Tribal Hazard Mitigation Plans', 'tribal healthcare', 'Community Emergency Response Teams', 'CERT', 'climate resilience'], 
            'Energy': ['green policies', 'hydrogen', 'wind power', 'solar power', 'tidal power', 'renewable energy', 'alternative fuels', 'ethanol subsidies', 'synthetic fuel', 'oil', 'Petroleum', 'renewables', 'nuclear energy', 'energy strategy', 'Department of Energy', 'energy supply and conservation', 'global energy', 'long-range energy planning', 'electricity', 'coal', 'conservation', 'public utility', 'Nuclear Regulatory Commission', 'nuclear power', 'power plant'], 
            'Environmental Protection': ['pollution', 'Resources Protection Act', 'radioactive materials', 'climate change', 'greenhouse gases',  'solid waste management', 'recycling', 'energy policy', 'Environmental Protection Agency ',  'Council on Environmental Quality ', 'Energy Research and Development Association ', 'Clean Air Act', 'National Environmental Policy Act', 'EPA regulations'], 
            'Families': ['adoption law',  'child welfare', 'family welfare', 'welfare services', 'domestic abuse',  'child abuse', 'social welfare', 'family planning', 'Roe v. Wade', 'Planned Parenthood', 'violence against children', 'sexual exploitation', 'teenage pregnancy', 'teenage suicide', 'elderly abuse'], 
            'Finance and Financial Sector': ['Federal Reserve', 'Department of Commerce', 'National Bureau of Standards', 'federal regulation', 'Interstate Commerce Act', 'savings and loan associations', 'federal savings and loan associations', 'Truth-in-Lending Act', 'Securities Exchange Commission', 'Commodity Futures Trading Commission', 'Securities Exchange Act', 'Public Utility Holding Company Act', 'credit control act'], 
            'Foreign Trade and International Finance': ['global politics', 'allies', 'emergency food assistance', 'Peace Corps', 'Foreign Assistance Act', 'foreign assistance', 'foreign loans', 'international monetary system', 'international banking', 'trade agreements', 'customs enforcement', 'foreign investment'], 
            'Government Operations and Politics': ['elections', 'voting regulations', 'campaign funding', 'political action committees', 'government jobs', 'public servants', 'bureaucracy', 'Postal Service', 'presidential administration', 'political campaigns', 'civil service', 'Freedom of Information Act', 'FOIA', 'presidential appointments', 'whistleblowers', 'Federal Register', 'political parties', 'opinion polls', 'regulatory agencies', 'election laws'], 
            'Health': ['health care', 'disease prevention', 'health services administration', 'healthcare funding', 'Medicare', 'Medicaid',  'health facilities', 'medical research', 'healthcare access', 'healthcare quality', 'public health', 'healthcare disparities', 'patient care', 'health policy', 'healthcare reform', 'healthcare delivery', 'healthcare costs', 'healthcare regulation', 'tribal health system', 'Indian Self-Determination and Education Assistance Act', 'behavioral health', 'mental health', 'tribal clinic', 'tribal hospital', 'Indian Health Service', 'Indian hospitals', 'Indian doctors', 'reservation clinics', 'American Lung Association'], 
            'Housing and Community Development': ['Native American housing', 'American Indian homeownership', 'Tribal housing', 'Indian Housing Block Grant', 'tribal lands', 'rural housing', 'Self-Determination Act', 'NAHASDA', 'housing sovereignty', 'housing discrimination', 'homeownership', 'fair housing', 'housing infrastructure', 'housing conditions', 'affordable housing', 'homelessness', 'housing industry', 'foreclosure', 'home equity', 'housing market', 'house insurance', 'home insurance', 'affordable housing', 'home appraisal'], 
            'Immigration': ['naturalization', 'citizenship', 'immigrants', 'refugees', 'political asylum', 'Citizenship and Immigration Services'], 
            'International Affairs': ['civil war', 'foreign aid', 'human rights', 'international law', 'national governance', 'arms control', 'trade agreements', 'foreign investment', 'foreign loans', 'foreign trade', 'international finance', 'global politics', 'allies', 'emergency food assistance', 'Peace Corps', 'foreign assistance', 'house delegation', 'soviet union', 'ussr', 'Brezhnev', 'Ceaușescu', 'Josip Tito', 'Yugoslavia', 'Congressional Delegation', 'Delegation for International Affairs', 'foreign relations'], 
            'Labor and Employment': ['retirement age', 'age discrimination', 'ageism', 'early retirement', 'elderly discrimination', 'mandatory retirement', 'employment equality', 'Older Workers Benefit Protection Act', 'pension plan', 'pension plan protection', 'Pension Benefit Guaranty Corporation', 'employee leave sharing', 'unemployment compensation', 'federal employee benefits', 'social security', 'joblessness', 'employment rate', 'low wages', 'unemployment', 'unionizing', 'labor union'],
            'Native Americans': ['Oklahoma Enabling Act', 'Indian Homesteading', 'Mcgirt', 'Five Civilized Tribes', 'reparations', 'Indian Removal', 'Indian Claims Commission Act', 'Indian Claims Commission', 'Tee-Hit-Ton Indians', 'Creek Nation v. United States', 'General Allotment Act', 'tribal sovereignty', 'Indian affairs', 'Bureau of Indian Affairs', 'tribal advisory', 'Indian Civil Rights Act', 'global alphabet', 'Clean Water Act', 'Clean Air Act', 'Indian Child Welfare Act', 'Standing Rock Reservation', 'Thomas-Rogers Act', 'Treaty of Hopewell', 'Treaty of Fort Wayne', 'Indian Removal Act', 'Fort Laramie Treaty', 'Treaty of Fort Laramie', 'Dawes Act', 'Reconstruction Act', 'Forced Relocation', 'Self-Determination and Education Assistance Act', 'Termination Act',  'Johnson OMalley Act', 'Indian Land Consolidation Act', 'Indian Reorganization Act', 'Indian Citizenship Act', 'Americans for Indian Opportunity', 'Native American Graves Protection', 'Repatriation Act', 'Insular Affairs'], 
            'Public Lands and Natural Resources': ['leasing of federal lands', 'federal land', 'wilderness', 'water rights', 'mineral rights', 'public land', 'zoning', 'city boundaries', 'local statutes', 'local ordinances', 'parks and recreation', 'landmarks', 'historic land', 'historic building', 'land rights', 'treaties',  'Indian Claims Commission Act', 'Indian Claims Commission', 'Tee-Hit-Ton Indians', 'Creek Nation v. United States', 'General Allotment Act', 'state park', 'public park', 'Farmland Protection', 'Land Trust', 'Mineral Rights', 'Mining Regulation', 'Recreation Permit', 'Land Development', 'Urban Planning', 'national park', 'state park', 'city park', 'Wildlife Habitat'], 
            'Science, Technology, Communications': ['software', 'natural science', 'space exploration', 'research policy', 'research funding', 'Science, Technology, Engineering, and Mathematics', 'STEM', 'telecommunication', 'information technology', 'journalists', 'journalism', 'NASA', 'National Aeronautics and Space Administration',  'space program', 'National Advisory Committee for Aeronautics'], 
            'Social Sciences and History': ['social policy', 'archaeological research', 'historic sites', 'civil rights movements', 'historical sites', 'historical buildings', 'census', 'cultural heritage', 'social science research', 'public history', 'history education', 'minority studies', 'historical preservation', 'minority education'], 
            'Social Welfare': ['welfare reform', 'social deprivation', 'social programs', 'welfare state', 'public assistance', 'social security', 'federal aid', 'social insurance', 'retirement benefits', 'Social Security Administration', 'government aid'], 
            'Sports and Recreation': ['Bureau of Outdoor Recreation', 'youth recreation', 'amateur athletics', 'sports', 'gaming', 'stadium', 'outdoor activities', 'professional athletics', 'professional sports', 'sports license', 'professional sport', 'amateur sport'], 
            'Taxation': ['tax exemption', 'tax-exempt', 'tax break', 'Internal Revenue Service', 'IRS', 'state taxes', 'tax code', 'state regulations', 'state tax', 'tax bracket', 'tax deduction', 'income tax', 'Sovereign Tax', 'tax collection'], 
            'Transportation and Public Works': ['AMTRAK', 'light rail system', 'rail transportation', 'public bus', 'public transportation', 'National Highway Transportation Safety Administration', 'highways', 'highway safety', 'traffic issue', 'public transportation', 'National Transportation Safety Board', 'Federal Aviation Administration', 'Civil Aeronautics Board', 'Interstate Commerce Commission', 'mass transit', 'Department of Transportation', 'Federal Highway Administration', 'Federal Motor Carrier Safety Administration', 'Federal Railroad Administration', 'Federal Transit Administration', 'National Highway Traffic Safety Administration', 'National Railroad Passenger Corporation', 'seatbelt', 'seat belt', 'road construction', 'highway construction', 'traffic light'], 
            'Water Resources Development': ['drinking water', 'water pollution', 'lead contamination', 'water conservation', 'Land and Water Conservation Fund', 'soil conservation', 'water rights', 'water dam', 'river dam', 'water project', 'Clean Water Act', 'water resource', 'safe drinking water', 'Water supply', 'wastewater', 'flood control', 'flood'],

        }
        
        matching_policies = set()
        summary_lower = summary.lower()
        text_lower = text.lower()

        for policy, keywords in predefined_policies.items():
            for keyword in keywords:
                if keyword.lower() in summary_lower or keyword.lower() in text_lower:
                    matching_policies.add(policy)

        return list(matching_policies) if matching_policies else ['No Policy Assigned']

    # Function to assign party affiliation
    def assign_party(summary):
        predefined_parties = {
            'Independence Party': ['independence party'],
            'Alliance Party': ['alliance party'],
            'American Independent Party': ['american independent party'],
            'Christian Democratic Union': ['christian democratic union'],
            'Christian Pro-Life Party': ['christian pro-life party'],
            'Citizens Party': ['citizens party'],
            'Communist Party': ['communist party'],
            'Concerned Citizens Party': ['concerned citizens party'],
            'Conservative': ['conservative'],
            'Conservative Party': ['conservative party'],
            'Constitution Party': ['constitution party'],
            'Democratic': ['james jones', 'james r. jones', 'john f. kennedy', 'jfk', 'ted kennedy', 'robert f. kennedy', 'robert s. kerr', 'clinton', 'carter', 'al gore', 'glenn english', 'helen gahagan douglas', 'j. howard edmondson', 'percy gassaway', 'thomas gore', 'fred harris', 'josh lee', 'dave mccurdy', 'robert owen', 'robert l. owen', 'tom steed', 'william stigler', 'mike synar', 'elmer thomas', 'wickersham', 'democratic party'],
            'Democratic Socialists of America': ['democratic socialists of america'],
            'Grassroots Party': ['grassroots party'],
            'Green Party': ['green party'],
            'Independent': ['independent'],
            'Labor Party': ['labor party'],
            'Liberal Party': ['liberal party'],
            'Libertarian': ['libertarian'],
            'National Socialist Movement': ['national socialist movement'],
            'Natural Law': ['natural law'],
            'Patriot Party': ['patriot party'],
            'Peoples Party': ['peoples party'],
            'Progressive': ['progressive'],
            'Progressive Labor Party': ['progressive labor party'],
            'Reform Party': ['reform party'],
            'Republican': ['republican party', 'ronald reagan', 'reagan', 'george bush', 'bellmon', 'socialist party', 'united citizens party', 'working families party', 'bartlett', 'happy camp', 'mickey edwards', 'istook', 'steve largent', 'j.c. watts', 'jc watts', 'dick armey'],
            'Communist Party of the Soviet Union': ['Brezhnev', 'Russian Communist Party', 'Vladimir Lenin', 'Stalin', 'Khrushchev', 'Gorbachev', 'Chernenko'],
            'League of Communists of Yugoslavia': ['Josip Tito', 'Filipovic', 'Markovic', 'Doronjski', 'Krunic'],
            'Romanian Communist Party ': ['Ceausescu']
        }
        
        found_parties = [party for party, keywords in predefined_parties.items() for keyword in keywords if keyword.lower() in summary.lower()]
        return found_parties or ['No Party Assigned']

    # Function to map dates to congress year ranges
    def map_date_to_congress(dates):
        congresses = {
            '50th Congress (1887-1889)':   ('1887-3-04', '1889-3-03'),
            '51st Congress (1889-1891)':   ('1889-3-04', '1891-3-03'),
            '52nd Congress (1891-1893)':   ('1891-3-04', '1893-3-03'),
            '53rd Congress (1893-1895)':   ('1893-3-04', '1895-3-03'),
            '54th Congress (1895-1897)':   ('1895-3-04', '1897-3-03'),
            '55th Congress (1897-1899)':   ('1897-3-04', '1899-3-03'),
            '56th Congress (1899-1901)':   ('1899-3-04', '1901-3-03'),
            '57th Congress (1901-1903)':   ('1901-3-04', '1903-3-03'),
            '58th Congress (1903-1905)':   ('1903-3-04', '1905-3-03'),
            '59th Congress (1905-1907)':   ('1905-3-04', '1907-3-03'),
            '60th Congress (1907-1909)':   ('1907-3-04', '1909-3-03'),
            '61st Congress (1909-1911)':   ('1909-3-04', '1911-3-03'),
            '62nd Congress (1911-1913)':   ('1911-3-04', '1913-3-03'),
            '63rd Congress (1913-1915)':   ('1913-3-04', '1915-3-03'),
            '64th Congress (1915-1917)':   ('1915-3-04', '1917-3-03'),
            '65th Congress (1917-1919)':   ('1917-3-04', '1919-3-03'),
            '66th Congress (1919-1921)':   ('1919-3-04', '1921-3-03'),
            '67th Congress (1921-1923)':   ('1921-3-04', '1923-3-03'),
            '68th Congress (1923-1925)':   ('1923-3-04', '1925-3-03'),
            '69th Congress (1925-1927)':   ('1925-3-04', '1927-3-03'),
            '70th Congress (1927-1929)':   ('1927-3-04', '1929-3-03'),
            '71st Congress (1929-1931)':   ('1929-3-04', '1931-3-03'),
            '72nd Congress (1931-1933)':   ('1931-3-04', '1933-3-03'),
            '73rd Congress (1933-1935)':   ('1933-3-04', '1935-1-03'),
            '74th Congress (1935-1937)':   ('1935-1-03', '1937-1-03'),
            '75th Congress (1937-1939)':   ('1937-1-03', '1939-1-03'),
            '76th Congress (1939-1941)':   ('1939-1-03', '1941-1-03'),
            '77th Congress (1941-1943)':   ('1941-1-03', '1943-1-03'),
            '78th Congress (1943-1945)':   ('1943-1-03', '1945-1-03'),
            '79th Congress (1945-1947)':   ('1945-1-03', '1947-1-03'),
            '80th Congress (1947-1949)':   ('1947-1-03', '1949-1-03'),
            '81st Congress (1949-1951)':   ('1949-1-03', '1951-1-03'),
            '82nd Congress (1951-1953)':   ('1951-1-03', '1953-1-03'),
            '83rd Congress (1953-1955)':   ('1953-1-03', '1955-1-03'),
            '84th Congress (1955-1957)':   ('1955-1-03', '1957-1-03'),
            '85th Congress (1957-1959)':   ('1957-1-03', '1959-1-03'),
            '86th Congress (1959-1961)':   ('1959-1-03', '1961-1-03'),
            '87th Congress (1961-1963)':   ('1961-1-03', '1963-1-03'),
            '88th Congress (1963-1965)':   ('1963-1-03', '1965-1-03'),
            '89th Congress (1965-1967)':   ('1965-1-03', '1967-1-03'),
            '90th Congress (1967-1969)':   ('1967-1-03', '1969-1-03'),
            '91st Congress (1969-1971)':   ('1969-1-03', '1971-1-03'),
            '92nd Congress (1971-1973)':   ('1971-1-03', '1973-1-03'),
            '93rd Congress (1973-1975)':   ('1973-1-03', '1975-1-03'),
            '94th Congress (1975-1977)':   ('1975-1-03', '1977-1-03'),
            '95th Congress (1977-1979)':   ('1977-1-03', '1979-1-03'),
            '96th Congress (1979-1981)':   ('1979-1-03', '1981-1-03'),
            '97th Congress (1981-1983)':   ('1981-1-03', '1983-1-03'),
            '98th Congress (1983-1985)':   ('1983-1-03', '1985-1-03'),
            '99th Congress (1985-1987)':   ('1985-1-03', '1987-1-03'),
            '100th Congress (1987-1989)':  ('1987-1-03', '1989-1-03'),
            '101st Congress (1989-1991)':  ('1989-1-03', '1991-1-03'),
            '102nd Congress (1991-1993)':  ('1991-1-03', '1993-1-03'),
            '103rd Congress (1993-1995)':  ('1993-1-03', '1995-1-03'),
            '104th Congress (1995-1997)':  ('1995-1-03', '1997-1-03'),
            '105th Congress (1997-1999)':  ('1997-1-03', '1999-1-03'),
            '106th Congress (1999-2001)':  ('1999-1-03', '2001-1-03'),
            '107th Congress (2001-2003)':  ('2001-1-03', '2003-1-03'),
            '108th Congress (2003-2005)':  ('2003-1-03', '2005-1-03'),
            '109th Congress (2005-2007)':  ('2005-1-03', '2007-1-03'),
            '110th Congress (2007-2009)':  ('2007-1-03', '2009-1-03'),
            '111th Congress (2009-2011)':  ('2009-1-03', '2011-1-03'),
            '112th Congress (2011-2013)':  ('2011-1-03', '2013-1-03'),
            '113th Congress (2013-2015)':  ('2013-1-03', '2015-1-03'),
            '114th Congress (2015-2017)':  ('2015-1-03', '2017-1-03'),
            '115th Congress (2017-2019)':  ('2017-1-03', '2019-1-03'),
            '116th Congress (2019-2021)':  ('2019-1-03', '2021-1-03'),
            '117th Congress (2021-2023)':  ('2021-1-03', '2023-1-03'),
            '118th Congress (2023-2025)':  ('2023-1-03', '2025-1-03'),
        }
        
        unique_congresses = set()
        
        for date in dates:
            # Parse the date
            date_obj = dateparser_parse(date)
        
            # Skip if the date cannot be parsed (returns None)
            if not date_obj:
                print(f"Warning: Unable to parse date '{date}'")
                continue

            # Compare the parsed date with Congress date ranges
            for congress, (start_date, end_date) in congresses.items():
                start_date_obj = dateparser_parse(start_date)
                end_date_obj = dateparser_parse(end_date)
            
            # Check if the parsed date falls within the Congress date range
            if start_date_obj and end_date_obj and start_date_obj <= date_obj <= end_date_obj:
                unique_congresses.add(congress)

        return list(unique_congresses)

    # Initialize lists to store data
    filenames = []  
    summaries = []  
    creators = []  
    recipients = []  
    subjects_list = []  
    dates_list = []  
    named_entities_list = []  
    states_list = []  
    tribes_list = []  
    policies_list = []  
    parties_list = []  
    titles_list = []  
    tribal_organizations_list = []
    congress_list = []
    tribal_leaders_list = []
    tribal_sovereignty_cases_list = []
    allotment_cases_list = []
    property_rights_cases_list = []
    tribal_reservations_cases_list = []
    tribal_citizenship_cases_list = []
    taxation_cases_list = []
    american_indian_claims_list = []

# Iterate through .txt files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            time.sleep(DELAY_BETWEEN_REQUESTS)

            try:
                title = generate_title(content)
                summary = generate_summary(content)
                creator, recipient = analyze_summary(summary)
                policies = assign_policy(summary, content)
                parties = assign_party(summary)
                extracted_tribes = extract_tribes(content)
                tribal_organizations = extract_tribal_organizations(extracted_tribes)
                states = extract_states(content)
                dates = extract_dates(content)
                named_entities = extract_named_entities(content)
                subjects = assign_subjects(content)
                found_leaders_with_tribes = find_and_tag_tribal_leaders(content)
                categorized_cases = categorize_legal_cases(content)

                # Append data to each list
                filenames.append(file_path)
                summaries.append(summary)
                creators.append(creator)
                recipients.append(recipient)
                subjects_list.append(subjects)
                dates_list.append(dates)
                named_entities_list.append(named_entities)
                states_list.append(states)
                tribes_list.append(extracted_tribes)
                policies_list.append(policies)
                parties_list.append(parties)
                titles_list.append(title)
                tribal_organizations_list.append(tribal_organizations)
                congress_list.append(map_date_to_congress(dates))
                tribal_leaders_list.append(found_leaders_with_tribes)
                tribal_sovereignty_cases_list.append(categorized_cases['Tribal Sovereignty Cases'])
                allotment_cases_list.append(categorized_cases['Allotment Cases'])
                property_rights_cases_list.append(categorized_cases['Property Rights Cases'])
                tribal_reservations_cases_list.append(categorized_cases['Tribal Reservations Cases'])
                tribal_citizenship_cases_list.append(categorized_cases['Tribal Citizenship Cases'])
                taxation_cases_list.append(categorized_cases['Taxation Cases'])
                american_indian_claims_list.append(categorized_cases['American Indian Claims'])

            except Exception as e:
                print(f"Error processing transcript {file_path}: {e}")
                
                # Append None or empty values for all lists to maintain consistent length
                filenames.append(file_path)
                summaries.append(None)
                creators.append(None)
                recipients.append(None)
                subjects_list.append(None)
                dates_list.append(None)
                named_entities_list.append(None)
                states_list.append(None)
                tribes_list.append(None)
                policies_list.append(None)
                parties_list.append(None)
                titles_list.append(None)
                tribal_organizations_list.append(None)
                congress_list.append(None)
                tribal_leaders_list.append(None)
                tribal_sovereignty_cases_list.append(None)
                allotment_cases_list.append(None)
                property_rights_cases_list.append(None)
                tribal_reservations_cases_list.append(None)
                tribal_citizenship_cases_list.append(None)
                taxation_cases_list.append(None)
                american_indian_claims_list.append(None)

    # Create a pandas DataFrame to store the results
    df = pd.DataFrame({
        'Filename': filenames,
        'Summary': summaries,
        'Creator': creators,
        'Recipient': recipients,
        'Subjects': subjects_list,
        'Dates': dates_list,
        'Named Entities': named_entities_list,
        'States': states_list,
        'Tribes': tribes_list,
        'Policies': policies_list,
        'Parties': parties_list,
        'Titles': titles_list,
        'Tribal Organizations': tribal_organizations_list,
        'Congress': congress_list,
        'Tribal Leaders': tribal_leaders_list,
        'Tribal Sovereignty Cases': tribal_sovereignty_cases_list,
        'Allotment Cases': allotment_cases_list,
        'Property Rights Cases': property_rights_cases_list,
        'Tribal Reservations Cases': tribal_reservations_cases_list,
        'Tribal Citizenship Cases': tribal_citizenship_cases_list,
        'Taxation Cases': taxation_cases_list,
        'American Indian Claims': american_indian_claims_list
    })

    # Export to Excel
    df.to_excel(output_excel_file, index=False)
    print(f"Data saved to {output_excel_file}")

if __name__ == "__main__":
    main()
