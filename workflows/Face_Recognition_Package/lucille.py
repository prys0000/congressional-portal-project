import os
import face_recognition
import pickle

# Path to the root folder containing subfolders of identified face images
identified_faces_root_folder = r'add your path here to the Oklahoma_Images_TestGroup'

# Create a dictionary to store face encodings and their labels
face_encodings = {}

# Traverse the root folder
for subdir, dirs, files in os.walk(identified_faces_root_folder):
    for file in files:
        if file.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(subdir, file)
            label = os.path.basename(subdir)  # Use the subfolder name as the label
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                if label not in face_encodings:
                    face_encodings[label] = []
                face_encodings[label].append(encoding[0])

# Save the encodings to a file
with open('G:/face_encodings.pkl', 'wb') as f:
    pickle.dump(face_encodings, f)

print("Annotated face encodings have been saved.")
