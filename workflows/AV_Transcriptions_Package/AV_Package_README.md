**Set-Up Instructions and Batch Process for Pipeline**

Below are the instructions to set up the environment and run the pipeline using the provided scripts. This includes a `set-up.bat` file and a batch process to execute the scripts in order.

---

### **`set-up.bat`**

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

:: Set environment variables if necessary (e.g., add ffmpeg to PATH)

echo Setup complete.
pause
```

**Note**: The `choco` command requires [Chocolatey](https://chocolatey.org/), a package manager for Windows. If you don't have it installed, you can download ffmpeg manually or install Chocolatey from [https://chocolatey.org/install](https://chocolatey.org/install).

---

### **Instructions for Setting Up OpenAI API Key**

1. **Set OpenAI API Key as Environment Variable**

   It's recommended to set your OpenAI API key as an environment variable for security. You can do this by running the following command in your command prompt:

   ```batch
   setx OPENAI_API_KEY "your-api-key-here"
   ```

   Replace `"your-api-key-here"` with your actual OpenAI API key.

2. **Modify Scripts to Use Environment Variable**

   Update `step3_describe_keyframes.py` and `step4_summarize_vids_parallel.py` to read the API key from the environment variable.

   Replace the line:

   ```python
   MY_OPENAI_API_KEY = "Replace-With-Your-API-Key"
   ```

   with:

   ```python
   import os
   MY_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   if not MY_OPENAI_API_KEY:
       raise Exception("Please set the OPENAI_API_KEY environment variable.")
   ```

   Also, make sure to `import os` at the beginning of the scripts if it's not already imported.

---

### **Batch Process (`run_pipeline.bat`)**

```batch
@echo off
echo Running pipeline...

:: Set number of processes (adjust as needed)
set NUM_PROCESSES=4

:: Ensure required directories exist
if not exist "pres_ad_videos" (
    echo "Error: Directory 'pres_ad_videos' not found. Please place your video files in this directory."
    pause
    exit /b 1
)

:: Step 1: Transcribe videos
echo Running step 1: Transcribe videos
mpiexec -n %NUM_PROCESSES% python step1_transcribe_vids_parallel.py

:: Check for errors
if errorlevel 1 (
    echo "Error occurred in step 1."
    pause
    exit /b 1
)

:: Step 2.1: Extract keyframes via speech segments
echo Running step 2.1: Extract keyframes via speech segments
mpiexec -n %NUM_PROCESSES% python step2.1_extract_keyframes_viaspeechsegments.py

if errorlevel 1 (
    echo "Error occurred in step 2.1."
    pause
    exit /b 1
)

:: Step 2.2: Extract keyframes at regular intervals
echo Running step 2.2: Extract keyframes at regular intervals
mpiexec -n %NUM_PROCESSES% python step2.2_extract_keyframes_regularintervals.py

if errorlevel 1 (
    echo "Error occurred in step 2.2."
    pause
    exit /b 1
)

:: Step 3: Describe keyframes
echo Running step 3: Describe keyframes
mpiexec -n %NUM_PROCESSES% python step3_describe_keyframes.py

if errorlevel 1 (
    echo "Error occurred in step 3."
    pause
    exit /b 1
)

:: Step 4: Summarize videos
echo Running step 4: Summarize videos
mpiexec -n %NUM_PROCESSES% python step4_summarize_vids_parallel.py

if errorlevel 1 (
    echo "Error occurred in step 4."
    pause
    exit /b 1
)

echo Pipeline complete.
pause
```

---

### **Additional Setup Instructions**

- **Python Installation**

  Ensure that Python 3.x is installed on your system and that the `python` command is available in your command prompt.

- **MPI Installation**

  - Download and install Microsoft MPI from the following link:

    [https://www.microsoft.com/en-us/download/details.aspx?id=57467](https://www.microsoft.com/en-us/download/details.aspx?id=57467)

  - After installation, make sure the `mpiexec` command is available in your command prompt.

- **ffmpeg Installation**

  - Download ffmpeg from:

    [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

  - Extract the ffmpeg binaries and add the `bin` directory to your system `PATH`.

- **OpenAI GPT-4 with Vision**

  - Note that GPT-4 with vision capabilities is currently only available to selected users and through the OpenAI API.

  - Ensure that your OpenAI API key has access to GPT-4 with vision capabilities. If not, you may need to adjust the scripts or request access.

- **Directory Structure**

  Ensure that the following directories are present:

  - **Input Directories:**

    - `pres_ad_videos`: Place your input video files (`.mp4` format) in this directory.

  - **Output Directories (will be created by scripts if they don't exist):**

    - `pres_ad_whisptranscripts_json`
    - `pres_ad_whisptranscripts_tsv`
    - `pres_ad_whisptranscripts_txt`
    - `keyframes_speechcentered`
    - `keyframes_regintervals`
    - `GPT_frame_descriptions_speechcentered`
    - `GPT_frame_descriptions_regintervals`
    - `GPT_video_summaries`

- **METADATA.csv**

  - Ensure that a file named `METADATA.csv` is present in the working directory. This file is required by some of the scripts.

---

### **Final Notes**

- Before running the pipeline, ensure that all the scripts are in the same directory as the batch files.

- Adjust the `NUM_PROCESSES` variable in `run_pipeline.bat` according to the number of CPU cores or processes you want to utilize.

- If any of the steps fail, refer to the error messages and ensure that all dependencies are correctly installed and configured.

- Remember to replace any placeholder text in the scripts (e.g., API keys) with your actual information.

- **Important**: The scripts use hardcoded paths and filenames. Ensure that the filenames and paths in your environment match those expected by the scripts.

---

By following these instructions and using the provided batch files, you should be able to set up the environment and run the pipeline to process your videos.

Let me know if you need further assistance.