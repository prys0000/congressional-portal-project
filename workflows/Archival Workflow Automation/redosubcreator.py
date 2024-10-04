import openai
import pandas as pd
import re
import json


def main():

    # Load config from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    # Set API key and file paths
    openai.api_key = config['openai_api_key']
    input_file = config['outputs']['2-gary-primed']  # Input from 2-gary-primed's output
    output_file_path = config['outputs']['redosubcreator']  # Final output for both creators and subjects

    # Controlled creators list
    controlled_creators = [
        'Acoya, Peggy, 1923-2020',
        'Albert, Carl Bert, 1908-2000',
        # ... (rest of the list)
    ]

    # Controlled subjects list
    controlled_subjects = [
        'Abortion--Law and legislation--United States',
        'Aeronautics--United States',
        # ... (rest of the list)
    ]

    # Function to assign creators using OpenAI
    def assign_creators_with_openai(description):
        prompt = (
            f"Given the following description:\n\n{description}\n\n"
            f"Assign up to three relevant creators from this list based on the description:\n"
            f"{', '.join(controlled_creators)}\n\n"
            "Please list the creators."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        assigned_creators = response['choices'][0]['message']['content'].strip()
        creator_list = re.split(r',|\n|;', assigned_creators)
        creator_list = [creator.strip() for creator in creator_list if creator.strip()]
        return '; '.join(creator_list[:3])

    # Function to assign subjects using OpenAI
    def assign_subjects_with_openai(description):
        prompt = (
            f"Given the following description:\n\n{description}\n\n"
            f"Assign up to three relevant subjects from this list:\n"
            f"{', '.join(controlled_subjects)}\n\n"
            "Please list the subjects."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        assigned_subjects = response['choices'][0]['message']['content'].strip()
        return assigned_subjects

    # Load Excel file and process
    df = pd.read_excel(input_file)

    # Apply creator and subject assignment
    df['Assigned Creators'] = df['Summary'].apply(assign_creators_with_openai)
    df['Assigned Subjects'] = df['Summary'].apply(assign_subjects_with_openai)

    # Save the updated DataFrame to Excel
    df.to_excel(output_file_path, index=False)
    print(f"Creators and Subjects assigned and saved to {output_file_path}")


if __name__ == "__main__":
    main()
