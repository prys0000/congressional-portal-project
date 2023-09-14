import os
import time
import pandas as pd
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from gensim import corpora, models
from gensim.parsing.preprocessing import preprocess_string

# 1. Train a model using the curated list of subjects
file_path = r'E:\handwritingtest-1\av transcriptions\subjects.xlsx'
df = pd.read_excel(file_path)

texts = [preprocess_string(subject) for subject in df['Subjects']]
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

num_topics = len(texts)
lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)


# Function to assign topics to text
def assign_topics_to_text(text, model, dictionary, max_topics=5):
    preprocessed = preprocess_string(text)
    bow = dictionary.doc2bow(preprocessed)
    topics = model[bow]
    topics_sorted = sorted(topics, key=lambda item: item[1], reverse=True)[:max_topics]
    return [df['Subjects'].iloc[topic[0]] for topic in topics_sorted]


# Transcribe videos and assign topics
folder_path = input("Enter the path of the folder containing the videos: ")
output_dir = os.path.join(folder_path, 'transcriptions')
os.makedirs(output_dir, exist_ok=True)

r = sr.Recognizer()
results = []

for video_file in [f for f in os.listdir(folder_path) if f.endswith('.mp4')]:
    video_path = os.path.join(folder_path, video_file)
    print(f"Processing: {video_file}")

    try:
        # Extract audio from video
        video = VideoFileClip(video_path)
        audio = video.audio
        audio_path = os.path.join(output_dir, f"temp_audio_{video_file}.wav")
        audio.write_audiofile(audio_path)

        # Explicitly close audio and video streams
        audio.close()
        video.close()

        # Delay to ensure the file is released
        time.sleep(3)

        # Transcribe audio
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            transcript = r.recognize_sphinx(audio_data)

            # Assign topics to the transcript
            assigned_topics = assign_topics_to_text(transcript, lda_model, dictionary)
            results.append({'Filename': video_file, 'Assigned Subjects': ', '.join(assigned_topics)})

            # Retry file deletion multiple times
            for _ in range(5):
                try:
                    os.remove(audio_path)
                    break
                except Exception as e:
                    print(f"Retry deleting {audio_path}")
                    time.sleep(2)

    except Exception as e:
        print(f"Error processing {video_file}: {e}")

# Convert results to a DataFrame and save
result_df = pd.DataFrame(results)
result_df.to_excel(r'path_to_save_results.xlsx', index=False)
