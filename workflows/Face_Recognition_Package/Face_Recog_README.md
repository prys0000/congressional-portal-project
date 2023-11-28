## Face_Recognition Package

This folder contains the entire downloadable package to aid in creating a working model to detect and identify political figures from older collections (not found in many modern models). 

1. Option one: download our basic training images (Oklahoma focused)
2. Option two: Create your own directory by:
    * Create a directory - The "images" directory contains subdirectories, each representing a different individual (person). Images can be in common formats like JPEG, PNG, TIFF, etc... Within each person's subdirectory, 
    you will find multiple images of that person's face.
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
3. Training, Validation, and Test Splits: Some datasets are further divided into training, validation, and test sets. In such cases, you might see subdirectories like "train," "val," and "test" within the "images" and "annotations" directories. This split helps in model training and evaluation.
4. Landmark or Keypoint Annotations: For more advanced tasks, datasets may include annotations for facial landmarks or keypoints, which are specific points on a face (e.g., eyes, nose, mouth). These annotations are often used for facial landmark detection tasks.
5. Optional - Attributes and Labels: Datasets may contain attributes or labels associated with each face, such as age, gender, ethnicity, emotion, or identity.
6. Find a face detection model (We use [FaceNet](https://arxiv.org/abs/1503.03832)) for a starting place for face verification and face clustering tasks, where the goal is to compare and recognize faces based on their embeddings (vectors) rather than annotating bounding boxes around individual faces in images.
    * Face detection libraries ([OpenCV](https://github.com/opencv/opencv) or [dlib](https://github.com/davisking/dlib)) detect the faces in each image, crop and align, to detect a dataset.
    * FaceNet will generate embeddings (through vectors) for each face/image.
    * If using labeled data you can apply this feature to associate known faces.
    * Using your new dataset, use FaceNet to create a *FaceNet model*.
    * Evaluate your model on small traning sets.
    * ***Note***:*You don't need XML annotations for bounding boxes in the context of FaceNet because it focuses on face recognition based on embeddings rather than object detection. Instead, you'll work with the embeddings 
    directly to compare and recognize faces.*
