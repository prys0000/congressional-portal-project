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
import logging
import speech_recognition as sr
from moviepy.editor import VideoFileClip

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.debug('This message will be logged to a file.')

# Initialize stemmer
stemmer = PorterStemmer()

sys.setrecursionlimit(10000)  # Set a higher value than the default

# Prompt for OpenAI API key
api_key = input("Enter your OpenAI API key: ")

# Prompt for the directory containing .txt files
input_directory = input("Enter the directory containing your .txt files: ")

# Initialize the OpenAI API client
openai.api_key = api_key

# Initialize spaCy NLP model for named entity recognition
nlp = spacy.load("en_core_web_sm")

# Define global variables and settings
DELAY_BETWEEN_REQUESTS = 1  # Delay in seconds between API calls
MAX_RETRIES = 3  # Maximum number of retries for API calls
RETRY_DELAY = 5  # Delay in seconds before retrying an API call

# Global definition of predefined tribes
predefined_tribes = [
    'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 
    'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Comanche', 
    'Creek', 'Delaware', 'Iowa', 'Kaw', 'Keetoowah', 'Kickapoo', 
    'Kiowa', 'Lenape', 'Miami', 'Modoc', 'Muscogee', 'Odawa', 
    'Osage', 'Otoe', 'Ottawa', 'Pawnee', 'Ponca', 'Potawatomi', 'Mescalero Apache', 
    'Potowatomie', 'Quapaw', 'Sac and Fox', 'Sauk', 'Seminole', 
    'Shawnee', 'Tonkawa', 'Wichita', 'Wyandot', 'Wyandotte', 'Chippewa', 'Chilocco', 'Navajo', 'Hopi', 'Menominee',
]

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
    text = re.sub(r'\s+', '', text).strip()  # Collapse multiple spaces and trim
    return text

# Create empty lists to store data
filenames = []  # Define the filenames list

summaries = []  # Define the summaries list

sentiment = []

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
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Create a title for the following text:\n{text}\nTitle:",
                max_tokens=35,
                n=1,
                stop=None,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except openai.error.OpenAIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API request failed, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise e

# Function to generate a summary using ChatGPT with retry handling
def generate_summary(text, max_summary_length=200):
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Summarize the following text:\n{text}\nSummary:",
                max_tokens=max_summary_length,
                n=1,
                stop=None,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except openai.error.OpenAIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API request failed, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise e

def analyze_summary(summary):
    # Patterns to match different formats
    patterns = [
        # Pattern for "writes to" or "from ... to ..." format
        r"(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s(?:of\s\w+\s)?(?:writes\sto|from)\s(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        # Pattern for "by ... to ..." format
        r"(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s(?:of\s\w+\s)?(by)\s(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\sto",
        # Pattern for "to ... by ..." format
        r"(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\sto\s(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s(?:of\s\w+\s)?(by)",
    ]

    for pattern in patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            creator = match.group(1).strip() if match.group(1) else None
            recipient = match.group(2).strip() if match.group(2) else None
            return creator, recipient

    return None, None

def analyze_sentiment(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Classify the sentiment of the following text as positive, negative, attacking, or neutral:\n{text}",
            max_tokens=60
        )
        sentiment = response.choices[0].text.strip().lower()
        return sentiment
    except openai.error.OpenAIError as e:
        print(f"Error in sentiment analysis: {e}")
        return "Error"

# Lists for storing additional data
creators = []
recipients = []
summaries = []
sentiments = []

# Function to assign subjects to transcripts based on keywords
def assign_subjects(transcript, max_subjects=3):
    keyword_subject_mapping = {
        		'Abortion Law and legislation (United States)': ['pro-choice', 'pro-life', 'reproductive rights', 'family planning', 'roe v. wade', 'planned parenthood', 'heartbeat bill', 'medical abortion', 'surgical abortion', 'elective abortion', 'therapeutic abortion', 'national right to life', 'sex education', 'birth control', 'roe vs. wade', 'roe v wade']
                , 'Advertising-Political': ['campaign advertisement',  'campaign commercial', 'political media', 'propaganda',  'political campaign communication', 'advertising', 'television ad', 'radio ad', 'associated press', 'press corp']
                , 'Aeronautics': ['aviation', 'federal aviation administration', 'air traffic control', 'aerospace',  'airplane pilot',  'Airport Improvement Program', 'National Airspace System', 'Unmanned Aircraft Systems', 'airspace', 'Transportation Security Administration', 'air travel', 'skylab']
                , 'African American': ['colored', 'afro american', 'afro-american', 'black man', 'black woman', 'black community', 'negro']
                , 'Age Discrimination': ['retirement age', 'age discrimination', 'ageism', 'early retirement', 'elderly discrimination', 'mandatory retirement', 'employment equality', 'older workers benefit protection act']
                , 'Agricultural laws and legislation': ['farming regulations', 'subsidies', 'public land', 'us department of agriculture',  'food and drug administration', 'agriculture and food act', 'national agricultural bargaining board', 'tobacco import trends', 'coffee export', 'mexican produce', 'agricultural trade development and assistance act', 'agricultural trade development', 'foreign trade', 'farm', 'farms', 'farmers', 'organic farming', 'organic farm']
                , 'Ambassadors, United States': ['foreign relations', 'envoy', 'embassy']
                ,  'American Indians (general)': ['Chilocco', 'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Comanche', 'Creek', 'Delaware', 'Iowa', 'Kaw', 'Keetoowah', 'Kickapoo', 'Kiowa', 'Lenape', 'Miami', 'Modoc', 'Muscogee', 'Odawa', 'Osage', 'Otoe', 'Ottawa', 'Pawnee', 'Ponca', 'Potawatomi', 'Potawatomie', 'Quapaw', 'Sac and Fox', 'Sauk', 'Seminole', 'Shawnee', 'Tonkawa', 'Wichita', 'Wyandot', 'Wyandotte', 'tribe', 'tribal', 'american indian', 'native american', 'principal chief', 'five civilized tribes', 'indians', 'five tribes', 'Intertribal', 'Insular Affairs', 'Chippewa']
                ,  'American Indian Claims': ['land rights', 'treaties', 'land dispute', 'Indian Claims Commission Act', 'Indian Claims Commission', 'Tee-Hit-Ton Indians', 'Creek Nation v. United States', 'General Allotment Act', 'Indian Civil Rights Act', 'Oklahoma Enabling Act', 'Indian Homesteading', 'Mcgirt', 'Five Civilized Tribes', 'Indian Removal', 'tribal sovereignty', 'Indian affairs', 'Bureau of Indian Affairs ', 'tribal advisory', 'Clean Water Act', 'Clean Air Act', 'Indian Child Welfare Act', 'Standing Rock Reservation', 'Thomas-Rogers Act', 'Treaty of Hopewell', 'Treaty of Fort Wayne', 'Indian Removal Act', 'Fort Laramie Treaty', 'Treaty of Fort Laramie', 'Dawes Act', 'Reconstruction Act', 'Forced Relocation', 'Self-Determination and Education Assistance Act', 'Termination Act', 'Indian Civil Rights Act', 'Johnson OMalley Act', 'Indian Land Consolidation Act', 'Indian Reorganization Act', 'Indian Citizenship Act', 'Americans for Indian Opportunity', 'Native American Graves Protection', 'Repatriation Act', 'Bureau of indian affairs']
                , 'Animal and Crop Disease, Pest Control and Domesticated Animal Welfare': ['animal mailing', 'pork industry', 'brucellosis', 'blackfly quarantine', 'pesticide residues', 'animal trapping']
                , 'Animals (general)': ['animal protection', 'wildlife conservation', 'habitat protection', 'veterinary medicine', 'endangered species', 'environmental protection', 'wildlife', 'endangered species protection act', 'gray wolf restoration', 'salmon conservation', 'domesticated animal', 'animal abuse', 'animal welfare', 'animal rights']
                , 'Anti-Government Activities': ['communism', 'subversive activities control act', 'black panther party', 'students for a democratic society', 'terrorism', 'communist', 'terrorist']
                , 'Appropriations and expenditures': ['federal budget', 'financial cycle', 'fiscal policy', 'allocations', 'capital expenditures', 'treasury', 'earmarks', 'economic stimulus', 'gross domestic product',  'appropriations committee', 'capital gains']
                , 'Arms Control': ['disarmament', 'nuclear weapons', 'chemical weapons', 'biological weapons', 'strategic arms limitation talk', 'strategic arms reduction treaty', 'intermediate-range nuclear forces treaty', 'chemical weapons convention', 'missile technology control regime ', 'arms races', 'cuban missile crisis', 'ballistic missiles']
                , 'Arts and Humanities': ['national education association', 'national endowment for the humanities', 'department of interior', 'national endowment for local arts', 'public broadcasting']
                , 'Astronautics': ['space exploration', 'space shuttle', 'space capsule', 'moon landing', 'challenger space', 'National Aeronautics and Space Administration', 'skylab', 'lunar gateway', 'space program', 'National Advisory Committee for Aeronautics']
                , 'Banking, Finance and Domestic Commerce': ['finance', 'federal reserve', 'interest', 'department of commerce', 'national bureau of standards', 'federal regulation', 'interstate commerce act', 'federal deposit insurance corporation', 'resolution trust corporation', 'savings and loan crisis', 'federal savings and loan insurance', 'insolvent savings and loan association', 'federal credit union act', 'bank holding company act', 'truth in lending act', 'federal reserve board', 'securities exchange commission', 'commodity futures', 'securities exchange act', 'public utility holding company act', 'credit control act', 'balanced budget', 'government regulation']
                , 'Bankruptcy (general)': ['chapter 11', 'bankruptcy code', 'municipal bankruptcy', 'bankruptcy court', 'chapter 13']
                , 'Biography': ['life story', 'memoir', 'chronicle', 'profile', 'biography', 'journal', 'diaries', 'diary', 'obituary']
                , 'Business (general)': ['commerce', 'entrepreneurship', 'trade', 'corporations', 'supply chain',  'manufacturing',  'bankruptcy'],
                'Labor and Jobs (general': ['employer', 'job market'],
                'Campaign Management': ['campaign donations', 'campaign fund', 'campaign fundraising', 'political action committee', 'Federal Election Commission', 'Center for Responsive Politics', 'consumer watchdog', 'elections', 'voters', 'voting rights', 'campaign finance', 'campaign advertisement', 'candidate debate']
                , 'Character (leans heavy on character and values)': ['integrity', 'morals', 'values', 'reputation']
                , 'Civil Defense and Homeland Security': ['civil reserve air fleet', 'federal civil defense act', 'nuclear warfare', 'federal fallout shelter', 'civil defense air raid shelter program', 'civil air patrol', 'department of homeland security',  'domestic terrorism prevention']
                , 'Civil Rights': ['civil rights', 'civil liberties', 'equal protection', 'fair housing initiatives', 'voting rights', 'right to vote', 'civil liberty', 'human rights', 'equal rights', 'equal opportunity', 'gay rights', '13th amendment', '14th amendment', 'black code', 'social justice', '15th amendment']
                , 'Civil service, United States': ['government jobs', 'public servants', 'bureaucracy', 'government jobs', 'public servants']
                , 'Constituent Correspondence': ['letters', 'feedback', 'community representation', 'letter to', 'letter from', 'received from', 'written to', 'constituent correspondence', 'constituent letter', 'constituent']
                , 'Corruption-General': ['bribery', 'scandal', 'integrity', 'Anti-corruption', 'American Anti-Corruption Act', 'Public Integrity Act']
                , 'Courts (United States)': ['judiciary', 'justice', 'trials', 'scotus', 'litigation', 'supreme court', 'court']
                , 'Crime (general)': ['criminal offense', 'law enforcement', 'criminal justice', 'domestic violence', 'conviction', 'murder', 'larceny', 'federal bureau of investigation', 'FBI', 'penal code', 'crime rate', 'recidivism', 'forensic', 'dna evidence',]
                , 'Democratic Party': ['democrats', 'progressives', 'Obamacare', 'dnc', 'democratic national committee', 'blue wave', 'rust belt', 'dodd-frank', 'affordable care act', 'deferred action for childhood arrivals', 'daca', 'bernie sanders', 'new deal', 'jfk', 'fdr', 'pro-choice', 'green new deal', 'democratic party', 'Clinton', 'Carter', 'Al Gore', 'john f. Kennedy', 'robert s. kerr', 'glenn english', 'helen gahagan douglas', 'j. howard edmondson', 'percy gassaway', 'thomas gore', 'fred harris', 'james r. jones', 'josh lee', 'dave mccurdy', 'robert owen', 'robert l. owen', 'tom steed', 'william stigler', 'mike synar', 'elmer thomas', 'wickersham']
                , 'Disability or Disease Discrimination': ['airline discrimination', 'insurance discrimination', 'mentally retarded', 'americans with disabilities act', 'airline discrimination',  'equality act', 'rehabilitation act']
                , 'Domestic Disaster Relief': ['federal emergency management agency', 'disaster planning', 'early warning system', 'drought relief', 'national fire academy', 'flood insurance', 'disaster mitigation']
                , 'Drugs (general)': ['pharmaceuticals', 'narcotics', 'prescriptions', 'illegal substances', 'prescription', 'medicine', 'Cocaine', 'Depressants', 'Cannabis', 'Marijuana', 'hallucinogenic']
                , 'Education': ['school', 'vocational school', 'education', 'literacy', 'illiteracy', 'college', 'university']
                , 'Elderly Issues and Elderly Assistance Programs': ['Medicare', 'Medicaid', 'older americans act', 'aging', 'retirees', 'geriatrics', 'older americans act', 'elderly care', 'meals on wheels', 'national institute on aging', 'adult protective services', 'alzheimer', 'memory care', 'Medicaid Waiver', 'elderly']
                , 'Electricity and Hydroelectricity': ['tennessee valley authority', 'bonneville power administration', 'electric power plant', 'hydroelectric power', 'utility payment reform', 'federal energy regulatory commission', 'rural electrification', 'electric cooperative', ' electric power', 'electric utility rate reform', 'smart grid']
                , 'Elementary and Secondary Education': ['federal elementary and secondary education program', 'safe schools act', 'charter school', 'preschool', 'standardized testing', 'no child left behind', 'even start education act', 'department of education', 'adult illiteracy', 'rural education initiatives', 'school lunch program', 'universal pre-k']
                , 'Employee Benefits': ['pension plan', 'pension benefit guarantee corporation', 'employee leave sharing', 'unemployment compensation', 'federal employee benefits']
                , 'Energy policy (United States)': ['green policies', 'wind power', 'solar power', 'tidal power', 'renewable energy', 'alternative fuels', 'ethanol subsidies',  'green policy',  'Petroleum',  'nuclear', 'department of energy', 'nuclear regulatory commission', 'energy goals', 'energy supply and conservation', 'global energy', 'long-range energy', 'energy advisory committee', 'power supply', 'fossil fuels', 'electricity', 'power company', 'power grid']
                , 'Environmental Protection': ['drain water', 'dust control', 'environmental protection agency', 'council on environmental quality', 'energy research and development association', 'erda', 'clean air', 'national environmental policy act', 'epa regulations', 'environmental crime', 'pollution management', 'new energy act', 'pollution control', 'Resources Protection Act', 'natural resources', 'environmental protection', 'clean water', 'toxic substance', 'air quality', 'water quality', 'air pollution', 'Emissions test', 'Floodwater', 'floodplain', 'gray water', 'Hazardous Waste',  'Injection Well', 'Landfill', 'Hazardous Air', 'Noxious Gas', 'Ozone Layer', 'radioactive', 'sewage treatment', 'Superfund', 'Wastewater', 'Wetlands', 'Waterborne Waste']
                , 'Ethnic Minority and Racial Group Discrimination': ['ku klux klan', 'desegregation', 'race based crime', 'racial wealth gap',  'racial profiling', 'civil rights act', 'civil rights movement', 'jim crow', 'segregation', 'national association for the advancement of colored people', 'anti-defamation league']
                , 'Family Issues and Domestic Violence': ['child abuse', 'national child search', 'child pornography', 'violence against children', 'sexual exploitation', 'domestic violence', 'teenage suicide', 'elderly abuse', 'human trafficking']
                , 'First Amendment Issues': ['freedom of speech', 'freedom of assembly', 'freedom of religion', 'freedom of the press', 'school prayer']
                , 'Fisheries and Fishing': ['commercial fishing', 'commercial fisheries', 'fishery conservation', 'fish trapping', 'fishing licenses', 'fishing quotas', 'fish farming', 'commercial fishing']
                , 'Flood control, United States': ['levees', 'dams', 'water management', 'flood insurance', 'Flood barriers', 'Flood mitigation', 'Erosion']
                , 'Food Inspection and Safety': ['animal drug residues', 'consumer seafood safety', 'food labeling requirements', 'grain inspection services', 'pesticide residues on fruit', 'food irradiation control act', 'meat grading standards', 'railroad food storage', 'food packaging', 'federal seed act']
                , 'Foreign relations': ['international war', 'world war', 'global politics', 'allies', 'peace corps', 'foreign assistance act', 'foreign assistance', 'foreign relations']
                , 'Gambling': ['casinos', 'sports betting', 'consumer product safety commission', 'cpsc', 'deceptive mailings and solicitations', 'consumer reporting', 'greyhound racing', 'boxing', 'interstate horse racing', 'antitrust', 'performance enhancing drugs', 'title ix', 'gaming law']
                , 'Gender Identity and Sexual Orientation Discrimination': ['gay', 'homosexual', 'sexual identity', 'sexual orientation', 'social security inequities', 'female salary inequities', 'sex discrimination regulations', 'same sex marriage', 'transgender rights', 'transgender', 'lgbt', 'lgbtq', 'same sex', 'same-sex']
                , 'Government Subsidies to Farmers and Ranchers Agricultural Disaster Insurance': ['crop pricing', 'farm subsidies', 'market demand', 'farm credit', 'agricultural disaster relief', 'farm loan and credit issues', 'crop insurance programs', 'federal milk supply', 'wheat programs', 'agricultural adjustment act', 'wool act', 'sugar act']
                , 'Gun Control': ['firearms', 'Automatic weapon', 'Semiautomatic weapon',  'second amendment', 'national rifle association', 'gun safety', 'Gun Control Act', 'Title II', 'Firearm Owners Protection Act', 'Assault weapon']
                , 'Hazardous Waste and Toxic Chemical Regulation Treatment and Disposal': ['hazardous waste', 'waste sites', 'department of transportation', 'landfills', 'nuclear waste', 'pesticides regulation', 'coal dust']
                , 'Health insurance (Law and legislation, United States)': ['optometry', 'dental insurance', 'cancer treatment', 'medicare', 'medicaid', 'insurance premium', 'private health insurance', 'medicare supplemental insurance', 'tax-free medical savings accounts', 'vision insurance', 'vision coverage', 'dental coverage']
                , 'Higher Education (United States)': ['universities', 'colleges', 'degrees', 'higher education act', 'student financial aid', 'national collegiate athletic association', 'student loan', 'historically black colleges and universities', 'montgomery gi bill', 'veterans education assistance', 'pell grant', 'national defense education act', 'sea grant', 'space grant', 'affirmative action']
                , 'Housing Law and legislation (United States)': ['section 8', 'united states department of housing and urban development', 'housing authority', 'habitat for humanity', 'home owners association', 'city council', 'section eight']
                , 'Human Rights': ['social rights', 'civil rights', 'genocide', 'torture', 'human trafficking', 'human rights treaties', 'social justice', 'advocacy', 'human rights watch', 'amnesty international']
                , 'Immigration': ['immigrant', 'refugees', 'political asylum', 'Citizenship and Immigration Services', 'immigration']
                , 'Industrial Policy': ['automobile manufacturing bailouts', 'industry revitalization', 'industrial productivity', 'industrial reorganization', 'technological industry']
                , 'Inflation and Interest Rates': ['inflation', 'inflation control', 'price index', 'cost of living', 'bureau of labor']
                , 'Insurance Regulation': ['insurance fraud', 'no-fault motor vehicle insurance', 'flood insurance', 'terrorism risk insurance']
                , 'Land use Law and legislation': ['zoning', 'city boundaries', 'local statute', 'local ordinance', 'museum', 'public park', 'landmark', 'historic land', 'historic building', 'historic site', 'historical site', 'local ordinance', 'museum', 'parks', 'landmark', 'historic land', 'historic building']
                , 'Mental Health and Cognitive Capacities': ['mental health services', 'mental health centers', 'autism spectrum disorders', 'alzheimer disease']
                , 'Military budget': ['defense spending']
                , 'Military education': ['rotc', 'reserve officers training corps', 'west point', 'the citadel', 'GI bill', 'G.I. Bill', 'Servicemens Readjustment Act']
                , 'Political conventions (United States)': ['democratic national convention', 'republican national convention']
                , 'Pollution and Conservation in Coastal Waterways': ['ocean dumping', 'cruise ship pollution', 'marine sanctuaries', 'coral reef system', 'columbia river water', 'coastal erosion', 'oil spill', 'watershed protection']
                , 'Price Control and Stabilization': ['price control', 'economic stabilization', 'emergency price controls']
                , 'Public health and Health care (United States)': ['health campaigns', 'disease prevention', 'community health', 'health care system', 'medicare', 'affordable care act', 'health care reform', 'hospital', 'obamacare', 'clinic', 'universal health', 'cdc', 'health campaigns', 'disease prevention', 'community health', 'universal health']
                , 'Religion': ['faith', 'spirituality', 'school prayer', 'church', 'god', 'methodist', 'catholic', 'lutheran', 'jewish', 'judaism', 'muslim', 'allah', 'jesus', 'christ', 'prayer', 'church', 'Separation of Church and State', 'evangelism ', 'christianity', 'first amendment', '1st amendment', 'Free Exercise Clause', 'prayer in school' ]
                , 'Republican Party': ['conservatives', 'right-wing', 'party platform', 'conservative', 'reagan', 'bush', 'mitch mcconnell', 'tea party', 'pro-life', 'conservative political action conference', 'republican national committee', 'reaganomics']
                , 'Retirement': ['pension', 'seniors', 'retirement planning', 'golden years', 'Estate planning', 'Elderly care', 'Pension fund', 'senior living', 'retirement age', 'individual retirement account', 'IRA', 'medicare', '401k', 'social security']
                , 'Right to Privacy and Access to Government Information': ['reproductive rights', 'worker records', 'police wiretapping', 'medical records', 'access to government records', 'disclosure and confidentiality', 'freedom of information act', 'foia', 'Privacy laws', 'privacy legislation', 'surveillance law', 'open government']
                , 'Rural health United States': ['rural clinics', 'healthcare access', 'country medicine', 'social medicine', 'rural health']
                , 'Small Business Issues': ['small business administration', 'small business credit', 'product liability', 'minority business program', 'disaster loan program', 'small business']
                , 'Special Education': ['behavioral disability', 'cognitive disability', 'disabled infants', 'disabled toddlers', 'education of the handicapped act', 'disabilities education act']
                , 'Special Interests (Political)': ['lobbyists', 'advocacy groups', 'political action committee', 'special interest group']
                , 'Species and Habitat Protection': ['forest protection', 'endangered species protection', 'gray wolf', 'spotted owls', 'exotic bird conservation', 'bald eagle', 'laboratory animals', 'fish and wildlife protection', 'marine mammal protection', 'bristol bay fisheries', 'sport fish restoration', 'wilderness refuge protection', 'poaching', 'national park service']
                , 'Speeches': ['oratory', 'presentations', 'rhetoric', 'public speaking', 'speech']
                , 'Substance Alcohol and Drug Abuse Treatment and Education': ['narcotics', 'alcoholism', 'alcoholic anonymous', 'prescription drug abuse', 'national minimum drinking age act', 'alcoholic beverage advertising act', 'drunk driving', 'narcan regulation', 'opioid epidemic', 'drug and alcohol rehabilitation', 'drug rehab', 'treatment center']
                , 'Taxation Law and legislation (Oklahoma State)': ['state taxes', 'internal revenue', 'state regulations', 'oklahoma taxes', 'oklahoma state taxes', 'oklahoma tax commission']
                , 'Taxation Law and legislation (United States)': ['Tax exemption', 'internal revenue service', 'federal tax', 'tax bracket', 'internal revenue code', 'income tax', 'tax deduction', 'income tax', 'tax commission', 'tax exempt', 'nonprofit', '501c']
                , 'Term Limits': ['tenure restrictions', 'political service duration', 'political service duration']
                , 'Terrorism': ['extremism', 'counter-terrorism', 'september 11th', 'murrah bombing', 'insurrection', 'bomb scare', 'cyber attack', 'chemical warfare', 'biological warfare', 'domestic terrorism', 'domestic terrorist']
                , 'Tobacco Abuse Treatment and Education': ['cigarette advertising', 'smoking health risks', 'smoking prevention', 'smoking education']
                , 'Tourism': ['tourism industry', 'national tourism program', 'passport', 'department of tourism', 'National Travel and Tourism Office', 'United States Travel and Tourism Administration']
                , 'Transportation': ['public transport', 'public transportation', 'national transportation safety board', 'federal aviation administration', 'civil aeronautics board', 'interstate commerce commission', 'mass transit', 'department of transportation', 'Federal Aviation Administration', 'Federal Motor Carrier Safety Administration', 'Federal Railroad Administration', 'Federal Transit Administration', 'National Highway Traffic Safety Administration', 'rail car', 'sleeper car', 'railroad', 'seat belt', 'seatbelt', 'busing', 'department of transportation', 'rail policy', 'pacific railroad', 'transcontinental railroad', 'highway act']
                , 'Unemployment': ['joblessness', 'employment rate', 'layoffs', 'low wage']
                , 'Labor Unions': ['labor organizations', 'collective bargaining', 'workers rights', 'unionizing', 'AFL-CIO', 'labor union', 'labor unions', 'National Education Association', 'Service Employees International Union', 'American Federation of State, County and Municipal Employees', 'Teamsters', 'United Food and Commercial Workers', 'United Auto Workers', 'United Steelworkers', 'American Federation of Teachers', 'International Brotherhood of Electrical Workers', 'Laborers International Union of North America', 'International Association of Machinists and Aerospace Workers', 'United Brotherhood of Carpenters and Joiners of America', 'National Association of Letter Carriers', 'International Association of Fire Fighters', 'National Postal Mail Handlers Union', 'Transport Workers Union of America']
                , 'Armed Forces (United States)': ['Active Guard and Reserve', 'deployment', 'military', 'army', 'navy', 'marines', 'military aviation', 'usaf', 'aerial warfare', 'military aviation', 'coast guard', 'army national guard', 'special forces', 'navy seal', 'reserve', 'national guard', 'marine corps']
                , 'Public Utilities': ['water company', 'electric company', 'gas company', 'Oklahoma Natural Gas', 'Oklahoma Gas and Electric',  'Public Service Company of Oklahoma', 'Oklahoma Electric Cooperative', 'utility company']
                , 'Veterans and Veteran Care': [ 'war veterans', 'military retirees', ' benefits', 'veteran rights', 'military service recognition', 'federal regulations', ' hospitals', 'veterans hospital', 'military benefits']
                , 'Vietnam War': ['viet cong', 'north vietnamese army', 'ho chi minh trail', 'tet offensive', 'cold war', 'mcnamara', 'my lai massacre', 'draft', 'agent orange', 'viet cong', 'north vietnamese army']
                , 'Vocational Education': ['vocational training', 'displaced homemakers', 'technical training', 'trade school', 'apprenticeship', 'work-based training', 'accreditation ', 'job placement', 'vocational education and training policy', 'career technology', 'vo-tech', 'vo tech', 'Job Training Partnership Act']
                , 'Voting': ['ballots', 'elections', 'suffrage', 'voters', 'ballot box', 'ballot boxes', 'voting age', 'voter age']
                , 'Waste Management': ['garbage', 'waste management', 'recycling', 'waste disposal', 'sewage treatment', 'trash collection', 'storm water runoff']
                , 'Water resources development Law and legislation (United States)': ['drinking water', 'water pollution', 'lead contamination', 'water conservation', 'Land and Water Conservation Fund', 'soil conservation', 'water rights', 'water dam', 'river dam', 'water project', 'Clean Water Act', 'water resource', 'safe drinking water', 'Water supply', 'wastewater']
                , 'White Collar Crime and Organized Crime': ['asian organized crime', 'racketeer influenced and corrupt organizations act', 'president’s commission on organized crime', 'credit card counterfeiting', 'corporate criminal liability', 'crime labor racketeering', 'money laundering', 'cyber-crime']
                , 'World War': ['global conflict', 'wwi', 'the great war', 'world war 1', 'world war 2', 'world war i', 'world war ii', 'wwii']
                , 'Youth': ['young people', 'adolescents', 'next generation', 'teens', 'young people']
                , 'Cherokee Nation': ['W.W. Keeler', 'Ross Swimmer', 'Wilma Mankiller', 'William hicks', 'John Ross', 'Big Tiger', 'Pathkiller', 'John Jolly', 'Nimrod Smith', 'Sampson Owl', 'John Tahquette', 'Jarret Blythe', 'Robert Youngdeer', 'Frank Boudinot', 'W.W. Keeler', 'WW Keeler', 'JB Milan', 'J.B. Milan', 'Eastern Band of Cherokee Indians', 'Cherokee Nation', 'Keetoowah Nighthawk Society', 'Cherokee freedmen', 'United Keetoowah Band of Cherokee Indians']
                , 'Choctaw Nation': ['Choctaw freedmen', 'Harry J.W. Belvin', 'Hollis E. Roberts', 'Joseph Kincaid', 'Peter Folsom', 'Green McCurtain', 'William F. Semple', 'William Semple', 'William A. Durant', 'Harry J. W. Belvin', 'Gary Batton', 'Hollis Roberts', 'David Burrage', 'Richard Branam', 'Dancing Rabbit Creek', 'Doaksville Constitution', 'Choctaw code talkers', 'Choctaw Nation']
                , 'Chickasaw Nation': ['Chickasaw Nation', 'Chikashshanompa', 'Overton James', 'Anoatubby', 'Charles W. Blackwell']
                , 'Creek Nation ': ['McGirt', 'Creek Nation', 'Muscogee Nation', 'Muscogee Confederacy', 'Claude Cox', 'Norman Hoyt', 'Robert L. Thomas', 'Gerald W. Hill', 'College of the Muscogee Nation', 'Creek Freedmen', 'Creek Council House', 'Samuel Chocote', 'Locher Harjo', 'Ward Coachman', 'Joseph M. Perryman', 'Legus Perryman', 'Edward Bullette', 'Sparhecher', 'Pleasant Porter', 'William McIntosh', 'Jim Pepper', 'Great Mortar', 'Yayatustenuggee', 'Opothleyaholo ', 'William Weatherford', 'Lamochattee']
                , 'Osage Nation': ['Osage Nation', 'Fred Lookout', 'Charles Tillman', 'John Red Eagle', 'Little Osage', 'James Bigheart', 'Shonka Sabe', 'Osage Allotment Act', 'Osage Indian murder', 'John Joseph Mathews', 'Killers of the Flower Moon', 'Osage Headrights', 'Bacone College', 'Osage Nation Museum', 'Tink Tinker', 'Chief White Hair', 'Maria Tallchief', 'Marjorie Tallchief']
                , 'Comanche Nation': ['Comanche Nation', 'Quanah Parker', 'Wallace Coffey', 'Shoshoni', 'Shoshone', 'Comanche Nation College', 'Comanche Code Talker', 'Charles Chibitty', 'Peta Nocona', 'White Parker', 'Jesse Ed Davis']
                , 'Kiowa Tribe': ['Kiowa Tribe', 'Clyde Mithlo', 'Phillip Jack Anquoe', 'Billy Evans Horse', 'J.T. Goombi', 'JT Goombi', 'Sitting Bear', 'Guipago', 'Satanta', 'Chief Lone Wolf', 'Kiowa Six', 'Ahpeahtone', 'Horace Poolaw', 'Pascal Poolaw', 'Jack Hokeah', 'Spencer Asah', 'James Auchiah', 'Chief Big Bow']
                , 'Pawnee Nation': ['Pawnee Nation', 'Andrew Knife Chief', 'Walter Echo-Hawk', 'Albert Gourd', 'Sun Chief', 'Sharitahrish', 'Big Spotted Horse', 'John Echohawk', 'Larry Echo Hawk', 'Petalesharo', 'Wicked Chief']
                , 'Sac and Fox Nation': ['Sac and Fox Nation', 'Charles Jordan ', 'George Thurman', 'Jack Williams', 'Jim Thorpe', 'Thakiwaki']
                , 'Seminole Nation': ['Coeehajo', 'Seminole Nation', 'George Harjo', 'Floyd Harjo', 'Richmond Tiger', 'Leonard Harjo']

        
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
def extract_tribes(text):
    # Define the list of predefined tribes
    predefined_tribes = [
        'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 
        'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Comanche', 
        'Creek', 'Delaware', 'Iowa', 'Kaw', 'Keetoowah', 'Kickapoo', 
        'Kiowa', 'Lenape', 'Miami', 'Modoc', 'Muscogee', 'Odawa', 
        'Osage', 'Otoe', 'Ottawa', 'Pawnee', 'Ponca', 'Potawatomi', 'Mescalero Apache', 
        'Potowatomie', 'Quapaw', 'Sac and Fox', 'Sauk', 'Seminole', 
        'Shawnee', 'Tonkawa', 'Wichita', 'Wyandot', 'Wyandotte', 'Chippewa', 'Chilocco', 'Navajo', 'Hopi', 'Menominee',
    ]
    
    # Convert the text to lowercase to ensure case-insensitive matching
    text_lower = text.lower()
    
    # Initialize an empty list to store extracted tribes
    extracted_tribes = []
    
    # Iterate through predefined tribes and check if they exist in the text
    for tribe in predefined_tribes:
        # Check if the tribe's name is in the text (case-insensitive)
        if tribe.lower() in text_lower:
            extracted_tribes.append(tribe)

    return extracted_tribes


# Function to extract tribal organizations from extracted tribes
def extract_tribal_organizations(extracted_tribes):
    # Define a mapping of tribes to tribal organizations
    tribal_organizations_mapping = {
        'Anadarko Agency', 'Chickasaw Agency', 'Concho Agency', 'Eastern Oklahoma Regional Office', 'Miami Agency', 'Okmulgee Agency', 'Osage Agency', 'Pawnee Agency', 'Southern Plains Regional Office', 'Wewoka Agency', 'Chickahominy Indians - Eastern Division', 'Northern Arapaho Business Council', 'Cataba Tribal Association', 'Northern Cherokee Nation of the Old Louisiana Territory', 'Northern Cherokee Tribe of Indians', 'Southeastern Cherokee Confederacy', 'United Band of the Western Cherokee Nation', 'Shawnee Indian Agency', 'Osage River Agency', 'Sac and Fox Agency in Kansas', 'Sac and Fox Agency in Indian Territory', 'Shawnee Agency', 'Western Oklahoma Consolidated Agency', 'Kiowa, Comanche, and Wichita Agency', 'Cheyenne and Arapaho Agency', 'Red Moon Agency', 'Western Superintendency', 'Five Civilized Tribes Agency', 'Dawes Commission', 'Shawnee Indian Agency', 'Western Oklahoma Consolidated Agency', 'Pawnee Agency', 'Ponca Agency', 'Otoe Agency', 'Kaw Subagency', 'Fort Sill Apache Tribe of Oklahoma', 'Sac Fox Nation, Oklahoma', 'Wyandotte Nation', 'Seminole Nation of Oklahoma', 'Delaware Tribe of Indians', 'Thlopthlocco Tribal Town', 'United Keetoowah Band of Cherokee Indians in Oklahoma', 'Choctaw Nation of Oklahoma', 'Miami Tribe of Oklahoma', 'Kickapoo Tribe of Oklahoma', 'Iowa Tribe of Oklahoma', 'Kiowa  Indian Tribe of Oklahoma', 'Delaware Nation, Oklahoma', 'Modoc Nation', 'Kialegee Tribal Town', 'Alabama-Quassarte Tribal Town', 'Comanche Nation, Oklahoma', 'Apache Tribe of Oklahoma', 'Cherokee Nation', 'Absentee-Shawnee Tribe of Indians of Oklahoma', 'Kaw Nation', 'Ottawa Tribe of Oklahoma', 'Ponca Tribe of Indians', 'Quapaw Nation', 'Peoria Tribe of Indians', 'Pawnee Nation of Oklahoma', 'Shawnee Tribe', 'Seneca-Cayuga Nation', 'Chickasaw Nation', 'Osage Nation', 'Muscogee Nation', 'Tonkawa Tribe', 'Wichita and Affiliated Tribes', 'Otoe-Missouria Tribe of Indians', 'Citizen Potawatomi Nation', 'Caddo Nation', 'Cheyenne and Arapaho Tribes', 'Chilocco Nation'
    }
    
    tribal_organizations = []

    # Iterate through extracted tribes and map them to organizations
    for tribe in extracted_tribes:
        if tribe in tribal_organizations_mapping:
            tribal_organizations.extend(tribal_organizations_mapping[tribe])

    # Remove duplicates and return as a list
    return list(set(tribal_organizations))


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
        "United States", "Canada", "Mexico", "Argentina", "London", "England"])
    
    # Filter out recognized countries from the recognized states
    filtered_states = [state for state in recognized_states if state not in recognized_countries]
    
    return filtered_states
    
# Function to assign policies from list   
def assign_policy(summary, text):
    global predefined_tribes
    predefined_policies = {
        'Agriculture and Food': ['US Department of Agriculture', 'Food and Drug Administration'], 
        'Animals': ['endangered species', 'animal welfare', 'marine protection', 'animal cargo', 'Exotic Wildlife', 'Animal Abuse', 'Animal Rights'], 
        'Armed Forces and National Security': ['national security', 'homeland security', 'department of homeland security', 'air patrol', 'civil defense'], 
        'Arts, Culture, Religion': ['Archaeological', 'Archaeology', 'national endowment for the humanities ', 'libraries', 'museum exhibit', 'cultural center', 'sound recording', 'motion picture',  'cultural property', 'cultural resource', 'cultural relations', 'religious freedom', 'separation of church and state'], 
        'Civil Rights and Liberties, Minority Issues': ['First Amendment', 'civil rights', 'civil disobedience', 'due process', 'abortion rights', 'minority health', 'equal rights', 'segregation', 'civil liberties', 'equal protection',  'fair housing',  'Indian Bill of Rights',  'National Indian Youth Council',  'cruel and unusual punishment', 'tribal sovereignty', 'National Indian Education Association ', 'American Indian Religious Freedom Act', 'Indian Appropriations', 'Indian Gaming Regulatory Act', 'Marshall Trilogy', 'fourteenth amendment ', '14th amendment', 'treaty of fort laramie', 'Oklahoma Enabling Act', 'Indian Citizenship Act', 'Nationality Act', 'domestic dependent nations', 'cultural assimilation', 'colonization', 'freedom of speech', 'peyote',  'equal education', 'Indian schools', 'Bureau of Indian Affairs ', 'voting rights', 'voting age'], 
        'Commerce': ['business law', 'business loans', 'small business', 'consumer protection', 'manufacturing',  'consumer affairs', 'trade practices', 'intellectual property', 'imports and exports', 'foreign trade', 'finance policy', 'tariff', 'monopoly'], 
        'Congress': ['congressional committee', 'congressional oversight',  'Legislative Lobbying', 'Policy Reform', 'Policy Amendment', 'Congressional Act', 'Acts of Congress', 'Legislative Measure','Congressional Sponsor'], 
        'Crime and Law Enforcement': ['criminal offenses', 'law enforcement',  'domestic violence', 'conviction', 'Federal Bureau of Investigation ', 'FBI', 'penal code', 'crime rate', 'recidivism', 'drug policy', 'criminal justice', 'juvenile court', 'gun control', 'witness protection', 'criminal justice oversight', 'sentencing reform', 'crime prevention'], 
        'Economics and Public Finance': ['budget appropriation', 'public debt', 'government lending', 'government account', 'monetary policy', 'economic theory', 'fiscal policy', 'tax reform', 'balanced budget', 'budget deficit', 'inflation', 'housing finance', 'gross domestic product', 'economic development', 'government bailout', 'central bank', 'global supply chain', 'free market'], 
        'Education': ['sequoyah system', 'global alphabet', 'Job Training Partnership Act',  'educational reform', 'federal elementary and secondary education program', 'Safe Schools Act', 'Department of Education', 'literacy', 'illiteracy', 'rural education initiative', 'Native American Education Act', 'Bureau of Indian Education', 'Tribal colleges and universities', 'Indian Education Act', 'Indian Education Policy Review', 'Native American Languages Act', 'Indian Self-Determination and Education Assistance Act', 'tribal education', 'Johnson-OMalley Act', 'Indian School Equalization Program', 'education disparities', 'Indigenous curriculum', 'language preservation', 'tribal schools', 'ICWA', 'Indian Child Welfare Act '], 
        'Emergency Management': ['Federal Emergency Management Agency ', 'FEMA', 'disaster planning', 'early warning system', 'drought relief', 'National Fire Academy', 'flood insurance', 'earthquake', 'disaster mitigation', 'disaster preparedness', 'Tribal Homeland Security Grant Program', 'Tribal Emergency Operations Centers', 'Tribal Hazard Mitigation Plans', 'tribal healthcare', 'Community Emergency Response Teams ', 'CERT', 'climate resilience'], 
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
        'Native Americans': ['Oklahoma Enabling Act', 'Indian Homesteading', 'Mcgirt', 'Five Civilized Tribes', 'reparations', 'Indian Removal', 'Indian Claims Commission Act', 'Indian Claims Commission', 'Tee-Hit-Ton Indians', 'Creek Nation v. United States', 'General Allotment Act', 'native American', 'indigenous peoples', 'native American', 'tribal health', 'tribal sovereignty', 'Indian affairs', 'Bureau of Indian Affairs ', 'tribal advisory', 'Indian Civil Rights Act', 'global alphabet', 'Clean Water Act', 'Clean Air Act', 'Indian Child Welfare Act', 'Standing Rock Reservation', 'Thomas-Rogers Act', 'Treaty of Hopewell', 'Treaty of Fort Wayne', 'Indian Removal Act', 'Fort Laramie Treaty', 'Treaty of Fort Laramie', 'Dawes Act', 'Reconstruction Act', 'Forced Relocation', 'Self-Determination and Education Assistance Act', 'Termination Act',  'Johnson OMalley Act', 'Indian Land Consolidation Act', 'Indian Reorganization Act', 'Indian Citizenship Act', 'Americans for Indian Opportunity', 'Native American Graves Protection', 'Repatriation Act', 'tribe', 'tribal', 'five civilized tribes', 'indian school', 'Absentee-Shawnee', 'Apache', 'Arapaho', 'Caddo', 'Cayuga', 'Cherokee', 'Cheyenne', 'Chickasaw', 'Choctaw', 'Chippewa', 'Comanche', 'Creek', 'Delaware', 'Iowa', 'Kaw', 'Keetoowah', 'Kickapoo', 'Kiowa', 'Lenape', 'Miami', 'Modoc', 'Muscogee', 'Odawa', 'Osage', 'Otoe', 'Ottawa', 'Pawnee', 'Ponca', 'Potawatomi', 'Potowatomie', 'Quapaw', 'Sac and Fox', 'Sauk', 'Seminole', 'Shawnee', 'Tonkawa', 'Wichita', 'Wyandot', 'Wyandotte', 'tribe', 'tribal', 'bureau of indian affairs', 'Chilocco', 'Insular Affairs'], 
        'Public Lands and Natural Resources': ['leasing of federal lands', 'federal land', 'wilderness', 'water rights', 'mineral rights', 'public land', 'zoning', 'city boundaries', 'local ordinances', 'parks and recreation', 'landmarks', 'historic land', 'historic building', 'land rights', 'treaties',  'Indian Claims Commission Act', 'Indian Claims Commission', 'Tee-Hit-Ton Indians', 'Creek Nation v. United States', 'General Allotment Act', 'state park', 'public park', 'Farmland Protection', 'Land Trust', 'Mineral Rights', 'Mining Regulation', 'Recreation Permit', 'Land Development', 'Urban Planning', 'national park', 'state park', 'city park', 'Wildlife Habitat'],
        'Science, Technology, Communications': ['software', 'natural science', 'space exploration', 'research policy', 'research funding', 'Science, Technology, Engineering, and Mathematics', 'STEM', 'telecommunication', 'information technology', 'journalists', 'journalism', 'NASA', 'National Aeronautics and Space Administration',  'space program', 'National Advisory Committee for Aeronautics'], 
        'Social Sciences and History': ['social policy', 'archaeological research', 'historic sites', 'civil rights movements', 'historical sites', 'historical buildings', 'census', 'cultural heritage', 'social science research', 'public history', 'history education', 'minority studies', 'historical preservation', 'minority education'], 
        'Social Welfare': ['welfare reform', 'social deprivation', 'social programs', 'welfare state', 'public assistance', 'social security', 'federal aid', 'social insurance', 'retirement benefits', 'Social Security Administration', 'government aid'], 
        'Sports and Recreation': ['Bureau of Outdoor Recreation', 'youth recreation', 'amateur athletics', 'sports', 'gaming', 'stadium', 'outdoor activities', 'professional athletics', 'professional sports', 'sports license', 'professional sport', 'amateur sport'], 
        'Taxation': ['tax exemption', 'tax-exempt', 'tax break', 'Internal Revenue Service ', 'IRS', 'state taxes', 'tax code', 'state regulations', 'state tax', 'tax bracket', 'tax deduction', 'income tax', 'Sovereign Tax', 'tax collection'], 
        'Transportation and Public Works': ['AMTRAK', 'light rail system', 'rail transportation', 'public bus', 'public transportation', 'National Highway Transportation Safety Administration', 'highways', 'highway safety', 'traffic issue', 'public transportation', 'National Transportation Safety Board', 'Federal Aviation Administration', 'Civil Aeronautics Board', 'Interstate Commerce Commission', 'mass transit', 'Department of Transportation', 'Federal Highway Administration', 'Federal Motor Carrier Safety Administration', 'Federal Railroad Administration', 'Federal Transit Administration', 'National Highway Traffic Safety Administration', 'National Railroad Passenger Corporation', 'seatbelt', 'seat belt', 'road construction', 'highway construction', 'traffic light'], 
        'Water Resources Development': ['drinking water', 'water pollution', 'lead contamination', 'water conservation', 'Land and Water Conservation Fund', 'soil conservation', 'water rights', 'water dam', 'river dam', 'water project', 'Clean Water Act', 'water resource', 'safe drinking water', 'Water supply', 'wastewater']      

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
def map_date_to_congress(date):
    # Define the congresses and their corresponding date ranges
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
		        
		# Generate a sentiment analysis for the summary
        sentiment = analyze_sentiment(summary)
		
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
        policies_list.append(policy)
        parties_list.append(party)
        tribal_organizations_list.append(tribal_organizations)
        sentiments.append(sentiment)

# Create a DataFrame
data = {
    'Filename': filenames,
    'Title': titles_list,
    'Summary': summaries,
    'Sentiment': sentiments,
    'Creator': creators,
    'Recipient': recipients,
    'Subjects': subjects_list,
    'Tribes': tribes_list,
    'Dates': dates_list,
    'Named Entities': named_entities_list,
    'States': states_list,
    'Policies': policies_list,
    'Parties': parties_list,
    'Tribal Organizations': tribal_organizations_list
}

df = pd.DataFrame(data)
df['Congress'] = df['Dates'].apply(lambda dates: map_date_to_congress(dates))

# Prompt for the output Excel file path
output_excel_file = input("Enter the path for the output Excel file (with .xlsx extension): ")

# Check if the file path has the correct extension
if not output_excel_file.endswith('.xlsx'):
    print("The file path does not have a .xlsx extension. Adding it automatically.")
    output_excel_file += '.xlsx'

# Export to Excel
try:
    df.to_excel(output_excel_file, index=False)
    print(f"Data saved to {output_excel_file}")
except Exception as e:
    print(f"An error occurred while saving the Excel file: {e}")