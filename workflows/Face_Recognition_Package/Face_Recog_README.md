## Face_Recognition Package

This folder contains the entire downloadable package to help create a working model to detect and identify political figures from older collections (not found in many modern models). This dataset combines manually selected images from the Carl Albert Center Collection and [Congressional Bioguide](http://bioguide.congress.gov/biosearch/biosearch.asp). 

* **Option one:** Download our basic training images (Oklahoma-focused) - [Download from this folder](https://www.dropbox.com/scl/fo/68q2316c06buj05laj6ns/AFHg7N-8tdALlzyRwXWV4JM?rlkey=kkhem25h4zre8vtzh5s3ireu9&st=918epzdp&dl=0)
    * **Folder *Oklahoma_Imags_TestGroup*** holds a small group of folders with the faces of Oklahoma-focused individuals.
    * **Folder *Test_folder_Unidentified_Images*** holds a small test group of images that you can use to test the base-level script to get comfortable with how the recognition works. 
&nbsp;

* **Employ ${\color{purple}lucille.py}$:** Use this option to test our library and get familiar with annotating and creating a starting place. The **script ${\color{purple}lucille.py}$** processes a folder containing subfolders of identified face images, generates face encodings for each image, and saves these encodings to a .pkl file. 
&nbsp;
    * Loads images from a specified directory and its subdirectories
    * Uses the face_recognition library to generate face encodings for each image.
    * Labels each encoding based on the name of the subdirectory containing the image.
    * Stores the labeled encodings in a dictionary.
    * Serializes the dictionary of encodings and saves it to a file for later use in face recognition tasks.
 &nbsp;
* **Next run ${\color{blue}leon.py}$:** This **script ${\color{blue}leon.py}$** performs face recognition on a set of images with unidentified people, using precomputed face encodings of identified people. The results are saved to an Excel file.
&nbsp;
    * First, the script loads the precomputed face encodings from a pickle file.
    * Flattens the dictionary of face encodings into two lists: one for the encodings and one for the corresponding labels.
    * Specifies the path to the folder containing images with unidentified people.
    * Loops through each file in the unidentified_faces_folder.
    * Loads the image and detects faces and their encodings.
    * Compares each face encoding with known face encodings.
    * If a match is found within the tolerance level, assigns the corresponding label. Otherwise, assigns "Unknown".
    * Calculates face distances and determines the best match.
    * Converts the results dictionary to a DataFrame.
    * Saves the DataFrame to an Excel file.
&nbsp;
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
* **Option two:** Create your own directory by:
&nbsp;

    * Create a directory - The "images" directory contains subdirectories, each representing a different individual (person). Images can be in common formats like JPEG, PNG, TIFF, etc... Within each person's subdirectory, 
    you will find multiple images of that person's face.
&nbsp; 
        * dataset_root/
        ├── Person1/
        │   ├── Person1-1.jpg
        │   ├── Person1-2.jpg
        │   ├── metadata.txt (or info.xml)
        ├── Person2/
        │   ├── Person2-1.jpg
        │   ├── Person2-2.jpg
        │   ├── metadata.txt (or info.xml)
        ├── ... 
&nbsp; 

* **Process Images:** use ${\color{purple}dave.py}$ to standardize the images - resize, re-aspect, flip, optimize, and save all into a new 'output' folder.
&nbsp;

* **Training, Validation, and Test Splits:** Some datasets are divided into training, validation, and test sets. In such cases, you might see subdirectories like "train," "val," and "test" within the "images" and "annotations" directories. This split helps in model training and evaluation.
&nbsp;

* **Landmark or Keypoint Annotations:** For more advanced tasks, datasets may include annotations for facial landmarks or key points, which are specific points on a face (e.g., eyes, nose, mouth). These annotations are often used for facial landmark detection tasks.
&nbsp;

* ***Optional:*** - Attributes and Labels: Datasets may contain attributes or labels associated with each face, such as age, gender, ethnicity, emotion, or identity.
&nbsp;

* **Find a face detection model (FaceNet):** (We use [FaceNet](https://arxiv.org/abs/1503.03832)) for a starting place for face verification and face clustering tasks, where the goal is to compare and recognize faces based on their embeddings (vectors) rather than annotating bounding boxes around individual faces in images.
&nbsp;

    * Face detection libraries ([OpenCV](https://github.com/opencv/opencv) or [dlib](https://github.com/davisking/dlib)) detect the faces in each image, crop, and align to detect a dataset.
    * FaceNet will generate embeddings (through vectors) for each face/image.
    * Using labeled data, you can apply this feature to associate known faces.
    * Using your new dataset, use FaceNet to create a *FaceNet model*.
    * Evaluate your model on small training sets.
    * ***Note***:*You don't need XML annotations for bounding boxes in the context of FaceNet because it focuses on face recognition based on embeddings rather than object detection. Instead, you'll work with the embeddings directly to compare and recognize faces.*
&nbsp;
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
* **Advanced training and directional detection:** This process will enhance face recognition by incorporating directional positions (like left, right, or straight)
&nbsp;
    * Manually add faces from Option 1 that are multidirectional angles of the individual:
&nbsp;
 
     <img src="https://www.dropbox.com/scl/fi/aokw2lpkof4pebxgf53yl/Carl-Albert-1.jpg?rlkey=d67jg1wzpbzqh9vs3621er4uf&st=x0zk6gl6&raw=1" alt="Dropbox Image" width="250" height="325">
  
   <img src="https://www.dropbox.com/scl/fi/5ox564mimprhc1cqea3s2/Carl-Albert-left-2.jpg?rlkey=39kmi87xxk5qlfl3dhd9mtpq5&st=zotyo7ty&raw=1" alt="Dropbox Image" width="275" height="325">
   
   <img src="https://www.dropbox.com/scl/fi/pmwq0vy1pqo1bmhiqvcgu/Carl-Albert-right-1.jpg?rlkey=v7l9bgiwv5cnpdpgbftc87s21&st=yb3pyebn&raw=1" alt="Dropbox Image" width="275" height="325">
  
  
  
