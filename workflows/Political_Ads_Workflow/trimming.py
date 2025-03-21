import os
import cv2
import glob
import logging
import time
from tqdm import tqdm
from logging.handlers import RotatingFileHandler
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import subprocess

# Set up logger
def setup_logger(log_file: str):
    logger = logging.getLogger("VideoTrimmer")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger("video_trimming.log")

# Detect first person in video using YOLO
def detect_first_person(video_path: str, yolo_weights: str, yolo_cfg: str, coco_names: str) -> float or None:
    net = cv2.dnn.readNetFromDarknet(yolo_cfg, yolo_weights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    with open(coco_names, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sample_rate = 10  # analyze every 10th frame

    first_person_frame = None

    for frame_index in range(0, frame_count, sample_rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            break

        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = scores.argmax()
                confidence = scores[class_id]
                if confidence > 0.5 and classes[class_id] == "person":
                    first_person_frame = frame_index
                    break
            if first_person_frame:
                break
        if first_person_frame:
            break

    cap.release()

    if first_person_frame is not None:
        return first_person_frame / fps
    else:
        return None  # signal that no person was found

def has_audio_activity_ffmpeg(video_path: str, silence_threshold="-50dB", min_duration="1"):
    """
    Uses FFmpeg to check if the video has audio above the threshold.
    Returns True if any non-silent audio is detected, False otherwise.
    """
    try:
        command = [
            "ffmpeg",
            "-i", video_path,
            "-af", f"silencedetect=noise={silence_threshold}:d={min_duration}",
            "-f", "null",
            "-"
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        output = result.stderr

        has_audio = "silence_start" not in output or "silence_end" in output
        logger.debug(f"{os.path.basename(video_path)} — Audio Activity Detected: {has_audio}")
        return has_audio

    except Exception as e:
        logger.error(f"FFmpeg audio check failed for {video_path}: {e}")
        return False

# Trim video using FFmpeg
def trim_video(input_video: str, start_time: float, end_time: float, output_path: str):
    try:
        ffmpeg_extract_subclip(input_video, start_time, end_time, targetname=output_path)
        logger.info(f"Trimmed: {os.path.basename(input_video)} → {output_path}")
    except Exception as e:
        logger.error(f"Failed to trim {input_video}: {e}")

# Main processing loop
def process_videos(video_dir: str, output_dir: str, yolo_weights: str, yolo_cfg: str, coco_names: str):
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(video_dir, "*.mp4"))

    for video_path in tqdm(files, desc="Processing videos"):
        try:
            base_name = os.path.basename(video_path)
            trimmed_path = os.path.join(output_dir, base_name)

            start = time.time()
            first_person_time = detect_first_person(video_path, yolo_weights, yolo_cfg, coco_names)
            detection_time = time.time() - start

            if first_person_time is None:
                logger.info(f"No person detected in {base_name}. Checking for audio activity.")
                if has_audio_activity_ffmpeg(video_path):
                    logger.info(f"Audio detected in {base_name}. Trimming first 5 minutes.")
                    first_person_time = 0
                else:
                    logger.info(f"No audio or person in {base_name}. Skipping.")
                    continue



            end_time = first_person_time + 300  # trim 5 minutes from detection (or beginning)

            logger.debug(f"{base_name} — Start: {first_person_time:.2f}s | End: {end_time:.2f}s | Detection Time: {detection_time:.2f}s")

            trim_video(video_path, first_person_time, end_time, trimmed_path)

        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")

# Main entry point
if __name__ == "__main__":
    video_directory = r"D:\NEH-PORTAL\videos" ##add your path
    output_directory = r"D:\NEH-PORTAL\Videos_trimmed" ## add your path
    yolo_weights = "yolov3.weights"
    yolo_cfg = "yolov3.cfg"
    coco_names = "coco.names"

    process_videos(video_directory, output_directory, yolo_weights, yolo_cfg, coco_names)
