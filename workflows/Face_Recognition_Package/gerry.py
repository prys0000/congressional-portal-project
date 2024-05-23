import os
import face_recognition
import pickle
import pandas as pd

# Path to the folder containing identified face images
identified_faces_folder = r'add your path to identified images'

# Load directional annotations
annotations = pd.read_csv(r'add your path to the \annotations.csv')

# Debug: Print columns to verify
print("CSV Columns:", annotations.columns)

# Normalize filenames in annotations to ensure consistent matching
annotations['filename'] = annotations['filename'].apply(lambda x: x.lower())

# Create a dictionary to store face encodings, labels, and directions
face_encodings = {}

# Traverse the folder and process each image file
for file in os.listdir(identified_faces_folder):
    if file.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(identified_faces_folder, file)
        label = '_'.join(file.split('_')[:-1])  # Use the part of the filename before the last underscore as the label
        
        # Debug: Print label information
        print(f"Processing file: {file}, Label: {label}")

        normalized_file = file.lower()

        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            try:
                direction = annotations.loc[annotations['filename'] == normalized_file, 'direction'].values[0]
            except IndexError:
                print(f"Warning: No direction annotation found for {normalized_file}")
                continue

            if label not in face_encodings:
                face_encodings[label] = []
            face_encodings[label].append({
                'encoding': encoding[0],
                'direction': direction
            })

# Save the encodings to a file
with open(r'add where you want to save the \face_encodings_with_directions.pkl', 'wb') as f:
    pickle.dump(face_encodings, f)

print("Annotated face encodings with directions have been saved.")

# Print the total number of labels and their counts
print("Total number of labels:", len(face_encodings))
for label, encodings in face_encodings.items():
    print(f"Label: {label}, Number of encodings: {len(encodings)}")
