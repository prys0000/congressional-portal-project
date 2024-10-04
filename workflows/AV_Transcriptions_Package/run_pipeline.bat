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
mpiexec -n %NUM_PROCESSES% -wdir "%CD%" python step1_transcribe_vids_parallel.py "%VIDEO_DIR%" "%TRANSCRIPT_DIR%"

if errorlevel 1 (
    echo Error occurred in step 1.
    pause
    exit /b 1
)

:: Step 2.1: Extract keyframes via speech segments
echo Running step 2.1: Extract keyframes via speech segments
mpiexec -n %NUM_PROCESSES% -wdir "%CD%" python step2.1_extract_keyframes_viaspeechsegments.py "%VIDEO_DIR%" "%TRANSCRIPT_DIR%" "%KEYFRAMES_SPEECH_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 2.1.
    pause
    exit /b 1
)

:: Step 2.2: Extract keyframes at regular intervals
echo Running step 2.2: Extract keyframes at regular intervals
mpiexec -n %NUM_PROCESSES% -wdir "%CD%" python step2.2_extract_keyframes_regularintervals.py "%VIDEO_DIR%" "%KEYFRAMES_REG_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 2.2.
    pause
    exit /b 1
)

:: Step 3: Describe keyframes
echo Running step 3: Describe keyframes
mpiexec -n %NUM_PROCESSES% -wdir "%CD%" python step3_describe_keyframes.py "%KEYFRAMES_SPEECH_DIR%" "%KEYFRAMES_REG_DIR%" "%FRAME_DESC_SPEECH_DIR%" "%FRAME_DESC_REG_DIR%" "%TRANSCRIPT_DIR%" "%VIDEO_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 3.
    pause
    exit /b 1
)

:: Step 4: Summarize videos
echo Running step 4: Summarize videos
mpiexec -n %NUM_PROCESSES% -wdir "%CD%" python step4_summarize_vids_parallel.py "%FRAME_DESC_SPEECH_DIR%" "%FRAME_DESC_REG_DIR%" "%SUMMARY_DIR%" "%TRANSCRIPT_DIR%" "%VIDEO_DIR%" "%METADATA_FILE%"

if errorlevel 1 (
    echo Error occurred in step 4.
    pause
    exit /b 1
)

echo Pipeline complete.
pause
