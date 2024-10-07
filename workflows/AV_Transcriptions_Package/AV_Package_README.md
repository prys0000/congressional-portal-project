# Video Processing Pipeline Documentation

This project provides a comprehensive workflow for transcribing videos, extracting keyframes, describing those keyframes using OpenAI's GPT-4 (package 1) or with , and summarizing the videos.

This documentation will guide you through setting up the environment, running the pipeline, and understanding each step of the process.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
  - [Running the Pipeline](#running-the-pipeline)
- [Scripts Description](#scripts-description)
  - [Step 1: Transcribe Videos](#step-1-transcribe-videos)
  - [Step 2.1: Extract Keyframes via Speech Segments](#step-21-extract-keyframes-via-speech-segments)
  - [Step 2.2: Extract Keyframes at Regular Intervals](#step-22-extract-keyframes-at-regular-intervals)
  - [Step 3: Describe Keyframes](#step-3-describe-keyframes)
  - [Step 4: Summarize Videos](#step-4-summarize-videos)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This pipeline automates the process of:

1. **Transcribing Videos**: Uses the Whisper model (package 1) and Tesseract model (package 2)to transcribe video files.![image](https://github.com/user-attachments/assets/b91acdd8-873c-4fd3-ba2a-2b861e620e0f)
2. **Extracting Keyframes**:
   - Via speech segments.
   - At regular intervals.
3. **Describing Keyframes**: Utilizes GPT-4 to describe extracted keyframes.
4. **Summarizing Videos**: Generates summaries of videos based on transcripts and keyframe descriptions.

---

## Prerequisites

- **Operating System**: Windows (the batch scripts are designed for Windows Command Prompt).
- **Python**: Version 3.x installed and added to your system PATH.
- **Microsoft MPI**: For parallel processing.
- **ffmpeg**: For video processing.
- **OpenAI API Key**: Access to GPT-4 with vision capabilities.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/video-processing-pipeline.git
cd video-processing-pipeline
```

### 2. Set Up the Environment

Run the `set-up.bat` script to install necessary dependencies.

```batch
set-up.bat
```

**`set-up.bat`**:

```batch
@echo off
echo Setting up the environment...

:: Install necessary Python packages
pip install numpy pandas mpi4py openai opencv-python-headless glob2

:: Install Whisper (OpenAI's speech recognition model)
pip install git+https://github.com/openai/whisper.git

:: Install ffmpeg
echo Installing ffmpeg...
:: You can download ffmpeg from https://ffmpeg.org/download.html
:: For Windows, you can use a package manager like Chocolatey:
choco install ffmpeg -y

:: Install MPI
echo Installing MPI...
:: Download and install Microsoft MPI from:
:: https://www.microsoft.com/en-us/download/details.aspx?id=57467

echo Setup complete.
pause
```

**Note**: The `choco` command requires [Chocolatey](https://chocolatey.org/). If you don't have it installed, you can download ffmpeg manually.

### 3. Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```batch
setx OPENAI_API_KEY "your-api-key-here"
```

Replace `"your-api-key-here"` with your actual OpenAI API key.

---

## Directory Structure

Ensure the following directories are present:

- **Input Directories**:
  - `pres_ad_videos`: Place your input video files (`.mp4` format) here.
- **Required Files**:
  - `METADATA.csv`: Metadata file for the videos.
- **Output Directories** (will be created by the scripts if they don't exist):
  - `pres_ad_whisptranscripts`
  - `keyframes_speechcentered`
  - `keyframes_regintervals`
  - `GPT_frame_descriptions_speechcentered`
  - `GPT_frame_descriptions_regintervals`
  - `GPT_video_summaries`

---

## Usage

### Running the Pipeline

Use the `run_pipeline.bat` script to execute the pipeline. This script prompts you for necessary paths and runs each step sequentially.

```batch
run_pipeline.bat
```

**`run_pipeline.bat`**:

```batch
@echo off
echo Running pipeline...

:: Set number of processes (adjust as needed)
set NUM_PROCESSES=4

:: Prompt user for video directory
set /p VIDEO_DIR="Please enter the path to the directory containing the video files (e.g., pres_ad_videos): "

:: Ensure required directories exist
if not exist "%VIDEO_DIR%" (
    echo Error: Directory "%VIDEO_DIR%" not found. Please provide a valid directory.
    pause
    exit /b 1
)

:: Prompt for metadata file
set /p METADATA_FILE="Please enter the path to the metadata CSV file (e.g., METADATA.csv): "
if not exist "%METADATA_FILE%" (
    echo Error: File "%METADATA_FILE%" not found. Please provide a valid file.
    pause
    exit /b 1
)

:: Prompt user for output directories (or use default names)
set /p TRANSCRIPT_DIR="Please enter the path for the transcript output directory (default: pres_ad_whisptranscripts): "
if "%TRANSCRIPT_DIR%"=="" (
    set TRANSCRIPT_DIR=pres_ad_whisptranscripts
)

set /p KEYFRAMES_SPEECH_DIR="Please enter the path for speech-centered keyframes directory (default: keyframes_speechcentered): "
if "%KEYFRAMES_SPEECH_DIR%"=="" (
    set KEYFRAMES_SPEECH_DIR=keyframes_speechcentered
)

set /p KEYFRAMES_REG_DIR="Please enter the path for regular intervals keyframes directory (default: keyframes_regintervals): "
if "%KEYFRAMES_REG_DIR%"=="" (
    set KEYFRAMES_REG_DIR=keyframes_regintervals
)

set /p FRAME_DESC_SPEECH_DIR="Please enter the path for speech-centered frame descriptions (default: GPT_frame_descriptions_speechcentered): "
if "%FRAME_DESC_SPEECH_DIR%"=="" (
    set FRAME_DESC_SPEECH_DIR=GPT_frame_descriptions_speechcentered
)

set /p FRAME_DESC_REG_DIR="Please enter the path for regular intervals frame descriptions (default: GPT_frame_descriptions_regintervals): "
if "%FRAME_DESC_REG_DIR%"=="" (
    set FRAME_DESC_REG_DIR=GPT_frame_descriptions_regintervals
)

set /p SUMMARY_DIR="Please enter the path for video summaries directory (default: GPT_video_summaries): "
if "%SUMMARY_DIR%"=="" (
    set SUMMARY_DIR=GPT_video_summaries
)

:: Step 1: Transcribe videos
echo Running step 1: Transcribe videos
mpiexec -n %NUM_PROCESSES% python step1_transcribe_vids_parallel.py "%VIDEO_DIR%" "%TRANSCRIPT_DIR%"

if errorlevel 1 (
    echo Error occurred in step 1.
    pause
    exit /b 1
)

:: Step 2.1: Extract keyframes via speech segments
echo Running step 2.1: Extract keyframes via speech segments
mpiexec -n %NUM_PROCESSES% python step2.1_extract_keyframes_viaspeechsegments.py "%VIDEO_DIR%" "%TRANSCRIPT_DIR%" "%KEYFRAMES_SPEECH_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 2.1.
    pause
    exit /b 1
)

:: Step 2.2: Extract keyframes at regular intervals
echo Running step 2.2: Extract keyframes at regular intervals
mpiexec -n %NUM_PROCESSES% python step2.2_extract_keyframes_regularintervals.py "%VIDEO_DIR%" "%KEYFRAMES_REG_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 2.2.
    pause
    exit /b 1
)

:: Step 3: Describe keyframes
echo Running step 3: Describe keyframes
mpiexec -n %NUM_PROCESSES% python step3_describe_keyframes.py "%KEYFRAMES_SPEECH_DIR%" "%KEYFRAMES_REG_DIR%" "%FRAME_DESC_SPEECH_DIR%" "%FRAME_DESC_REG_DIR%" "%TRANSCRIPT_DIR%" "%VIDEO_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 3.
    pause
    exit /b 1
)

:: Step 4: Summarize videos
echo Running step 4: Summarize videos
mpiexec -n %NUM_PROCESSES% python step4_summarize_vids_parallel.py "%FRAME_DESC_SPEECH_DIR%" "%FRAME_DESC_REG_DIR%" "%SUMMARY_DIR%" "%TRANSCRIPT_DIR%" "%VIDEO_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 4.
    pause
    exit /b 1
)

echo Pipeline complete.
pause
```

#### Responding to Prompts

When running `run_pipeline.bat`, you'll be prompted for various paths. You can accept default values by pressing **Enter** or specify custom paths.

**Example Interaction**:

```
Please enter the path to the directory containing the video files (e.g., pres_ad_videos): C:\MyProject\pres_ad_videos

Please enter the path to the metadata CSV file (e.g., METADATA.csv): C:\MyProject\METADATA.csv

Please enter the path for the transcript output directory (default: pres_ad_whisptranscripts): [Press Enter]

Please enter the path for speech-centered keyframes directory (default: keyframes_speechcentered): [Press Enter]

Please enter the path for regular intervals keyframes directory (default: keyframes_regintervals): [Press Enter]

Please enter the path for speech-centered frame descriptions (default: GPT_frame_descriptions_speechcentered): [Press Enter]

Please enter the path for regular intervals frame descriptions (default: GPT_frame_descriptions_regintervals): [Press Enter]

Please enter the path for video summaries directory (default: GPT_video_summaries): [Press Enter]
```

**Note**: Brackets `[Press Enter]` indicate that you simply press the Enter key to accept the default value.

---

## Scripts Description

### Step 1: Transcribe Videos

**Script**: `step1_transcribe_vids_parallel.py`

- **Function**: Transcribes videos using OpenAI's Whisper model in parallel.
- **Input**:
  - Video files from the specified video directory.
- **Output**:
  - Transcripts in JSON, TSV, and TXT formats stored in the transcript output directory.

**Usage**:

```bash
mpiexec -n <num_processes> python step1_transcribe_vids_parallel.py <video_directory> <transcript_output_directory>
```

### Step 2.1: Extract Keyframes via Speech Segments

**Script**: `step2.1_extract_keyframes_viaspeechsegments.py`

- **Function**: Extracts keyframes from videos based on speech segments.
- **Input**:
  - Video files and corresponding transcripts.
- **Output**:
  - Keyframe images stored in the speech-centered keyframes directory.

**Usage**:

```bash
mpiexec -n <num_processes> python step2.1_extract_keyframes_viaspeechsegments.py <video_directory> <transcript_directory> <keyframe_output_directory> <metadata_csv>
```

### Step 2.2: Extract Keyframes at Regular Intervals

**Script**: `step2.2_extract_keyframes_regularintervals.py`

- **Function**: Extracts keyframes from videos at regular time intervals.
- **Input**:
  - Video files.
- **Output**:
  - Keyframe images stored in the regular intervals keyframes directory.

**Usage**:

```bash
mpiexec -n <num_processes> python step2.2_extract_keyframes_regularintervals.py <video_directory> <keyframe_output_directory> <metadata_csv>
```

### Step 3: Describe Keyframes

**Script**: `step3_describe_keyframes.py`

- **Function**: Describes keyframes using OpenAI's GPT-4 with vision capabilities.
- **Input**:
  - Keyframe images.
- **Output**:
  - Descriptions of keyframes stored in the frame descriptions directories.

**Usage**:

```bash
mpiexec -n <num_processes> python step3_describe_keyframes.py <speech_keyframe_dir> <reginterval_keyframe_dir> <speech_frame_desc_output_dir> <reginterval_frame_desc_output_dir> <transcript_dir> <video_dir> <metadata_csv>
```

### Step 4: Summarize Videos

**Script**: `step4_summarize_vids_parallel.py`

- **Function**: Summarizes videos based on transcripts and keyframe descriptions.
- **Input**:
  - Transcripts and keyframe descriptions.
- **Output**:
  - Summaries stored in the video summaries directory.

**Usage**:

```bash
mpiexec -n <num_processes> python step4_summarize_vids_parallel.py <speech_frame_desc_dir> <reginterval_frame_desc_dir> <summary_output_dir> <transcript_dir> <video_dir> <metadata_csv>
```

---

## Troubleshooting

- **Error: Directory Not Found**

  If you encounter an error stating a directory is not found, ensure that the path you provided exists and is correctly typed.

- **OpenAI API Key Issues**

  Ensure your API key is correctly set as an environment variable and that you have access to GPT-4 with vision capabilities.

- **ffmpeg Not Installed**

  If `ffmpeg` is not found, ensure it is installed and added to your system PATH.

- **MPI Issues**

  Ensure Microsoft MPI is installed and the `mpiexec` command is available.

- **Script Errors**

  Check the error messages for specifics and ensure all dependencies are installed. The scripts rely on certain Python packages and external tools.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## License

This project is licensed under the MIT License.

---

**Note**: This documentation assumes you have the necessary permissions and access to the required tools and APIs. Always ensure compliance with the terms of service of any third-party services used.

---

## Contact

For questions or support, please open an issue on the GitHub repository or contact the maintainer.
