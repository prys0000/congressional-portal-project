Script Notes: Topic Modeling and Audio Transcription from Videos

Imports:

Basic libraries such as os, time, and pandas are imported.
speech_recognition library is imported for transcribing audio.
moviepy.editor is used to extract audio from video files.
gensim is for topic modeling using the LDA algorithm.
Function Definitions:

assign_topic_lda(transcript, lda_model, dictionary):
Uses the trained LDA model to assign a topic to a given transcript.
Returns a string indicating the topic.
Initialization:

The speech recognition engine (Recognizer) is initialized.
User is prompted to provide the directory path where the video files are located.
An output directory (transcriptions) is set within the user-provided directory.
Transcribing Videos:

For each video in the provided directory:
The video file is loaded and the audio is extracted.
The audio is saved temporarily as a .wav file.
The audio is transcribed using the Sphinx recognizer from the speech_recognition library.
Transcriptions are stored in the all_transcripts list.
Temporary audio files are deleted to free up space.
Topic Modeling:

A Gensim dictionary is created from the transcribed data.
A Bag-of-Words (BoW) corpus is generated from the transcriptions using the dictionary.
An LDA model is trained on the corpus with a predefined number of topics (set as 5 in the script, but can be changed).
Each transcript is assigned a topic using the trained LDA model and the result is stored with the filename and transcript.
Saving the Results:

The filenames, their corresponding transcriptions, and assigned topics are saved to an Excel file (transcripts.xlsx) in the transcriptions directory.
Any errors during the process are printed to the console, allowing users to troubleshoot issues with specific video files or other parts of the process.
