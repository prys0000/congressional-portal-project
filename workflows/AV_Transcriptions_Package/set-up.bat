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
