import pandas as pd
import ast
import re


def preprocess_column_values(column):
    """Replace commas with semicolons, remove brackets and single quotes."""
    return column.str.replace(',', ';', regex=True).str.replace(r"[\[\]']", "", regex=True)
    
def preprocess_dates(date_series):
    """Convert string representations of lists to actual lists and find the oldest date."""
    def convert_dates(dates):
        if pd.isna(dates):
            return pd.NaT  # Return Not-A-Time for missing values
        try:
            date_list = ast.literal_eval(dates)  # Convert string to list
            # Convert to datetime, filtering out errors, and find the oldest date
            date_times = pd.to_datetime(date_list, errors='coerce')
            valid_dates = date_times.dropna()  # Remove NaT values that result from 'coerce'
            if valid_dates.empty:
                return pd.NaT  # Return NaT if there are no valid dates
            return min(valid_dates)
        except (ValueError, SyntaxError):
            return pd.NaT  # Return NaT in case of any exceptions during conversion
    
    return date_series.apply(convert_dates)

# Example usage
if __name__ == "__main__":
    # Load the data
    input_file = "add your transcript_info.xlsx"
    df = pd.read_excel(input_file, sheet_name="Sheet1")  # Ensure you use the correct sheet name

    # Preprocess dates and create new columns
    df['dcterms:date'] = preprocess_dates(df['Dates']).dt.strftime('%B %d, %Y')  # Human-readable format
    df['dcterms:created'] = preprocess_dates(df['Dates']).dt.strftime('%Y-%m-%d')  # ISO format

def add_indians_tribes(contributor):
    """Add 'Indians' after each tribe name in the 'Dcterms:Contributor' column."""
    if not pd.isnull(contributor):
        # Split by comma, add 'Indians', and then join back with semicolon
        tribes = [tribe.strip() + ' Indians' for tribe in contributor.split(',')]
        return '; '.join(tribes)
    return contributor

def extract_oldest_date(input_file, input_sheet, date_column, congress_column, output_column, output_file):
    # Read Excel file
    df = pd.read_excel(input_file, sheet_name=input_sheet)
    print(f"Initial DataFrame shape: {df.shape}")

    # Check for the existence of columns that will be processed or renamed - CUSTOMIZE THIS SECTION
    expected_columns = ['Dates', 'Filename', 'Congress', 'Tribes', 'Title', 'Summary', 'Creator', 'Subjects', 'Policies']
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the DataFrame.")

    # Apply preprocessing to the 'Dates' column
    df['dcterms:date'] = preprocess_dates(df['Dates']).dt.strftime('%B %d, %Y')
    df['dcterms:created'] = preprocess_dates(df['Dates']).dt.strftime('%Y-%m-%d')

    # Rename columns - CUSTOMIZE THIS SECTION
    df.rename(columns={
        'Filename': 'dcterms:identifier',
        'Congress': 'dcterms:temporal',
        'Tribes': 'Dcterms:Contributor',
        'Title': 'dcterms:title',
        'Summary': 'dcterms:description',
        'Creator': 'dcterms:creator',
        'Subjects': 'dcterms:http://purl.org/dc/terms/subject',
        'Policies': 'dcterms:subject',  
        # ... other renaming as needed ...
    }, inplace=True)

    # Strip '.txt' from the 'dcterms:identifier' column
    df['dcterms:identifier'] = df['dcterms:identifier'].str.replace('.txt', '', regex=False)

    # Apply preprocessing functions to the columns
    df['dcterms:temporal'] = preprocess_column_values(df['dcterms:temporal'])
    df['Dcterms:Contributor'] = df['Dcterms:Contributor'].apply(add_indians_tribes)


    # Set static column values - CUSTOMIZE THIS SECTION
    df['dcterms:provenance'] = 'Carl Albert Congressional Research and Studies Center, University of Oklahoma, Norman, OK'
    df['dcterms:rights'] = 'https://rightsstatements.org/page/NKC/1.0/?language=en'
    df['dcterms:language'] = 'eng'
    df['dcterms:type'] = 'correspondence'
    df['Dcterms:Type'] = 'text'
    df['dcterms:spatial'] = 'Oklahoma (State); United States (Nation)'

     # Define the correct order of columns - CUSTOMIZE THIS SECTION
    column_order = [
        'dcterms:provenance', 'dcterms:title', 'dcterms:date', 'dcterms:created',
        'dcterms:creator', 'dcterms:rights', 'dcterms:language', 'dcterms:temporal',
        'dcterms:relation', 'dcterms:isPartOf', 'dcterms:source', 'dcterms:identifier',
        'edm:preview', 'edm:isShownAt', 'dcterms:type', 'Dcterms:Type', 'dcterms:subject',
        'dcterms:description', 'dcterms:http://purl.org/dc/terms/subject',
        'Dcterms:Contributor', 'dcterms:spatial', 'dcterms:format', 'dcterms:publisher'
    ]
    
    # Drop specified columns - CUSTOMIZE THIS SECTION
    columns_to_drop = ['Recipient', 'Named Entities', 'States', 'Parties', 'Tribal Organizations', 'Tribal Leaders', 'New Congress', 'Oldest Date', 'Dates']
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    # Reorder columns to match the specified order and fill missing columns with NaN
    df = df.reindex(columns=column_order)

    # Write the updated DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print("Processing complete. Output saved to:", output_file)

# Example usage
input_file = "add your path to transcript_info.xlsx"
input_sheet = "Sheet1"
date_column = "Dates"
congress_column = "Congress"
output_column = "Oldest Date"
output_file = "add your path to create the new output.xlsx"

extract_oldest_date(input_file, input_sheet, date_column, congress_column, output_column, output_file)
