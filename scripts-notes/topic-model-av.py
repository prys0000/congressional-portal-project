import os
import time
import pandas as pd
import speech_recognition as sr
from moviepy.editor import VideoFileClip

# 1. Load subjects and keywords from CSV
subjects_df = pd.read_csv(r'E:\handwritingtest-1\typewriting-test-1\avpredefined_data.csv', encoding='ISO-8859-1')
topics = {}
for index, row in subjects_df.iterrows():
    combined_value = row[0]
    values = combined_value.split(',', 1)
    subject = values[0].strip()
    if len(values) > 1:
        keywords = values[1].strip().split()
    else:
        keywords = []
    topics[subject] = keywords


def assign_topic(transcript, topics):
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in transcript:
                return topic
    return "Unknown"


# 2. Initialize the recognizer and directories
r = sr.Recognizer()
folder_path = r'E:\handwritingtest-1\av transcriptions\Reagan'
output_dir = r'E:\handwritingtest-1\av transcriptions\Reagan\transcriptions'
os.makedirs(output_dir, exist_ok=True)
results = []

# 3. Process each video file
for video_file in [f for f in os.listdir(folder_path) if f.endswith('.mp4')]:
    video_path = os.path.join(folder_path, video_file)
    print(f"Processing: {video_file}")

    try:
        video = VideoFileClip(video_path)

        audio = video.audio
        audio_path = os.path.join(output_dir, f"temp_audio_{video_file}.wav")
        audio.write_audiofile(audio_path)
        audio.close()

        # Transcribe the audio
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            try:
                transcript = r.recognize_sphinx(audio_data)
                topic = assign_topic(transcript, topics)
                results.append({'Filename': video_file, 'Transcript': transcript, 'Topic': topic})
            except sr.UnknownValueError:
                print("Sphinx could not understand the audio")
            except sr.RequestError as e:
                print(f"Sphinx error: {e}")

            time.sleep(1)
            os.remove(audio_path)

    except Exception as e:
        print(f"Error processing {video_file}: {e}")
# 4. Check if the lengths of the two arrays are the same
if len([f for f in os.listdir(folder_path) if f.endswith('.mp4')]) == len(results):

    # 5. Save the results to an Excel file
    output_file = os.path.join(output_dir, 'transcripts.xlsx')
    try:
        df = pd.DataFrame(results, columns=['Filename', 'Transcript', 'Topic'])
        df.to_excel(output_file, index=False)
        print(f"Transcripts saved to {output_file}")
    except Exception as e:
        print(f"Error occurred while saving transcripts: {e}")
else:
    print("Error: Length mismatch between filenames and transcripts.")
