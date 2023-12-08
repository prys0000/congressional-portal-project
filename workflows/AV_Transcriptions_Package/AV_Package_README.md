## AV_Transcription_Package

This package automates the transcription of audio from video files, stores the transcriptions as TXT files (side-car), and compiles the results into an Excel file for easy access and analysis. It provides error handling and measures the execution time for monitoring script performance. Here's a summary of how it works:

* **Initialization:**

    * Script #1, ${\color{blue}allan.py}$ begins by importing necessary libraries, including os for file operations, speech_recognition for speech recognition, moviepy.editor for working with video and audio files, pandas for data handling, and time for measuring script execution time.

* **Recording Start Time:**

    * ${\color{blue}allan.py}$ records the start time to measure the execution time.

* **Recognizer Initialization:**

    * It initializes a speech recognizer using the speech_recognition library.

* **Folder Path and Output Directory:**

    * ${\color{blue}allan.py}$ specifies the folder path containing video files and creates an empty list, results, to store the transcription results.
    * It also defines an output directory where TXT files containing transcriptions will be saved.

* **Iterating Through Video Files:**

    * ${\color{blue}allan.py}$ iterates through the files in the specified folder.
    * For each video file, it performs the following steps:
    * Loads the video file using moviepy.
    * Extracts audio from the video.
    * Saves the extracted audio as a temporary WAV file.
    * Opens the audio file for speech recognition.

* **Speech Recognition:**

    * ${\color{blue}allan.py}$ uses Google Speech Recognition to transcribe the audio.
    * The transcribed text is stored in the transcript variable.

* **Storing Results:**

    * The filename and corresponding transcript are appended to the results list.
    * A TXT file is created for each transcript in the output directory.

* **Error Handling:**

    * ${\color{blue}allan.py}$ handles exceptions, such as UnknownValueError and RequestError, which can occur during transcription.
    * Temporary audio files are deleted after processing.

* **Data Validation:**

    * It checks if the number of processed files matches the number of results.

* **Creating a DataFrame:**

    * If the lengths match, ${\color{blue}allan.py}$ creates a pandas DataFrame with columns for filenames and transcripts.
    * An additional column for file names (without extensions) is added.

* **Saving Transcriptions:**

    * ${\color{blue}allan.py}$ saves the DataFrame as an Excel file in the specified output directory.
    * A message is printed to confirm the successful saving of transcripts.

* **Recording End Time:**

    * ${\color{blue}allan.py}$ records the end time and calculates the total execution time.
