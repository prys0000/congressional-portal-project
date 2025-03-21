import os 
import cv2
import glob
import logging
from tqdm import tqdm 
from logging.handlers import RotatingFileHandler
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Logger setup
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
def detect_first_person(video_path: str, yolo_weights: str, yolo_cfg: str, coco_names: str) -> float:
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

    first_person_frame = None
    sample_rate = 10  # Analyze every 5th frame

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
    return first_person_frame / fps if first_person_frame else 0

# Trim video using FFmpeg
def trim_video(input_video: str, start_time: float, end_time: float, output_path: str):
    try:
        ffmpeg_extract_subclip(input_video, start_time, end_time, targetname=output_path)
        logger.info(f"Trimmed video saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to trim video: {e}")
        raise

# Process videos
def process_videos(video_dir: str, output_dir: str, yolo_weights: str, yolo_cfg: str, coco_names: str):
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(video_dir, "*.mp4"))

    for video_path in tqdm(files, desc="Processing videos"):
        try:
            first_person_time = detect_first_person(video_path, yolo_weights, yolo_cfg, coco_names)
            start_time = max(first_person_time, 0)
            end_time = start_time + 300  # Limit to 5 minutes
            trimmed_path = os.path.join(output_dir, os.path.basename(video_path))
            trim_video(video_path, start_time, end_time, trimmed_path)
        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")

if __name__ == "__main__":
    video_directory = r"D:\   " # add the path to your source folder
    output_directory = r"D:\    # add the path to your output folder
    yolo_weights = "yolov3.weights"
    yolo_cfg = "yolov3.cfg"
    coco_names = "coco.names"
    
    process_videos(video_directory, output_directory, yolo_weights, yolo_cfg, coco_names)
