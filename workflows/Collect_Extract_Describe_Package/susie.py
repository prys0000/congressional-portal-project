import pandas as pd
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning, if present
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def check_and_save_links(excel_file, columns_to_check, output_file):
    # Read the Excel file
    df = pd.read_excel(excel_file)

    # Initialize status columns for each column to check
    for column_name in columns_to_check:
        status_column = f'Status_{column_name}'
        df[status_column] = ''

        # Ensure the specified column exists
        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in the Excel file.")
            continue

        # Iterate through each row and check the link
        for index, row in df.iterrows():
            link = row[column_name]

            try:
                # Set a timeout of 10 seconds, allow redirects, and disable SSL verification
                response = requests.head(link, timeout=10, allow_redirects=True, verify=False)

                print(f"Checking link in row {index + 2}: {link}")
                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    print(f"Link is working.")
                    df.at[index, status_column] = 'Yes'
                else:
                    print(f"Link is not working.")
                    df.at[index, status_column] = 'No'
            except Exception as e:
                print(f"Error checking link in row {index + 2}: {link} - {str(e)}")
                df.at[index, status_column] = 'Error'

    # Save the updated DataFrame to a new Excel file
    df.to_excel(output_file, index=False)

# Example usage
excel_file_path = "add your path to the new output.xlsx"
columns_to_check = ["edm:isShownAt", "edm:preview"]
output_excel_file = "add path to save the QC.xlsx"

check_and_save_links(excel_file_path, columns_to_check, output_excel_file)
