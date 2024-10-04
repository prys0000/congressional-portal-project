import pandas as pd
import os
import sys
import ast  # Don't forget to import ast module if used in preprocess_dates function

# Preprocess column values by replacing commas with semicolons and removing brackets and single quotes
def preprocess_column_values(column):
    column = column.astype(str)
    return column.str.replace(',', ';', regex=True).str.replace(r"[\[\]']", "", regex=True)

# Convert string representations of lists to actual lists and find the oldest date
def preprocess_dates(date_series):
    def convert_dates(dates):
        if pd.isna(dates):
            return pd.NaT
        try:
            date_list = ast.literal_eval(dates)
            date_times = pd.to_datetime(date_list, errors='coerce')
            valid_dates = date_times.dropna()
            return min(valid_dates) if not valid_dates.empty else pd.NaT
        except (ValueError, SyntaxError):
            return pd.NaT
    
    return date_series.apply(convert_dates)

# Add "Indians" after each tribe name in the 'Dcterms:Contributor' column
def add_indians_tribes(contributor):
    if not pd.isnull(contributor):
        tribes = [tribe.strip() + ' Indians' for tribe in contributor.split(',')]
        return '; '.join(tribes)
    return contributor

# Extract the filename without the path and extension
def extract_filename(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]

# Add the Assigned Creators and Assigned Subjects from the updated_excel_file
def merge_assigned_columns(df, updated_excel_file):
    # Load the updated Excel file
    updated_df = pd.read_excel(updated_excel_file)

    # Apply extract_filename to 'Filename' in updated_df to create 'dcterms:identifier'
    updated_df['dcterms:identifier'] = updated_df['Filename'].apply(extract_filename)

    # Ensure that the updated Excel file contains the necessary columns
    if 'Assigned Creators' in updated_df.columns and 'Assigned Subjects' in updated_df.columns:
        # Merge the columns from updated_df into the current DataFrame (df)
        df = df.merge(
            updated_df[['dcterms:identifier', 'Assigned Creators', 'Assigned Subjects']],
            on='dcterms:identifier',
            how='left'
        )
    else:
        print("Error: The updated_excel_file.xlsx does not contain 'Assigned Creators' or 'Assigned Subjects'.")

    return df


# Main function to process the DataFrame and save the output
def extract_oldest_date(input_file, input_sheet, updated_excel_file, output_file):
    df = pd.read_excel(input_file, sheet_name=input_sheet)
    print(f"Initial DataFrame shape: {df.shape}")

    if df.empty:
        print("The DataFrame is empty. No processing will be done.")
        return
    
    # Rename columns as needed
    df.rename(columns={
        'Filename': 'dcterms:identifier',
        'Congress': 'dcterms:temporal',
        'Tribes': 'Dcterms:Contributor',
        'Titles': 'dcterms:title',
        'Summary': 'dcterms:description',
        'Creator': 'dcterms:creator',
        'Subjects': 'dcterms:http://purl.org/dc/terms/subject',
        'Policies': 'dcterms:subject',  
        'Tribal Leaders': 'dcterms:triballeader',
    }, inplace=True)

    # Apply preprocessing functions
    df['dcterms:identifier'] = df['dcterms:identifier'].apply(extract_filename)
    df['dcterms:temporal'] = preprocess_column_values(df['dcterms:temporal'])
    df['Dcterms:Contributor'] = df['Dcterms:Contributor'].apply(add_indians_tribes)

    # Add static values
    df['dcterms:provenance'] = 'Carl Albert Congressional Research and Studies Center, University of Oklahoma, Norman, OK'
    df['dcterms:rights'] = 'https://rightsstatements.org/page/NKC/1.0/?language=en'
    df['dcterms:language'] = 'eng'
    df['dcterms:type'] = 'correspondence'
    df['Dcterms:Type'] = 'text'
    df['dcterms:spatial'] = 'Oklahoma (State); United States (Nation)'

    # Add Assigned Creators and Assigned Subjects from the updated_excel_file
    df = merge_assigned_columns(df, updated_excel_file)

    # Define the column order
    column_order = [
        'dcterms:provenance', 'dcterms:title', 'dcterms:date', 'dcterms:created',
        'dcterms:creator', 'dcterms:triballeader', 'dcterms:rights', 'dcterms:language',
        'dcterms:temporal', 'dcterms:relation', 'dcterms:isPartOf', 'dcterms:source',
        'dcterms:identifier', 'edm:preview', 'edm:isShownAt', 'dcterms:type', 'Dcterms:Type',
        'dcterms:subject', 'dcterms:description', 'dcterms:http://purl.org/dc/terms/subject',
        'Dcterms:Contributor', 'dcterms:spatial', 'dcterms:format', 'dcterms:publisher',
        'dcterms:cases1', 'dcterms:claims', 'dcterms:cases3', 'dcterms:cases4',
        'dcterms:cases5', 'dcterms:cases6', 'dcterms:cases7', 'Assigned Creators', 'Assigned Subjects'
    ]

    # Reorder columns and save to file
    df = df.reindex(columns=column_order)
    df.to_excel(output_file, index=False)
    print(f"Processing complete. Output saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python 3-POST-GOOD.py <input_file> <updated_excel_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    updated_excel_file = sys.argv[2]
    output_file = sys.argv[3]

    extract_oldest_date(input_file, "Sheet1", updated_excel_file, output_file)
