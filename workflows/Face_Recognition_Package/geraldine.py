import os
import face_recognition
import pickle
import pandas as pd
import numpy as np

# Load the face encodings
with open('add location to your /face_encodings_with_directions.pkl', 'rb') as f:
    known_face_encodings = pickle.load(f)

# Flatten the encoding list for comparison
flattened_encodings = []
flattened_labels = []
for label, encodings in known_face_encodings.items():
    for encoding in encodings:
        flattened_encodings.append(encoding['encoding'])
        flattened_labels.append(label)

# Path to the folder containing images with unidentified people
unidentified_faces_folder = r'add your path to the \unidentified_faces'

# Create a dictionary to store results
results = {}

for filename in os.listdir(unidentified_faces_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(unidentified_faces_folder, filename)
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(flattened_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(flattened_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            name = "Unknown"
            if matches[best_match_index]:
                name = flattened_labels[best_match_index]

            if filename not in results:
                results[filename] = []
            results[filename].append(name)

# Convert the results dictionary to a DataFrame
results_df = pd.DataFrame([(image, ', '.join(identified_faces)) for image, identified_faces in results.items()],
                          columns=['Image', 'Identified Faces'])

# Save the DataFrame to an Excel file
output_path = r'add the path where you want the \face_identification_results.xlsx'
results_df.to_excel(output_path, index=False)

print(f"Face identification completed. Results saved to {output_path}.")
