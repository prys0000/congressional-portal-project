@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.6 or higher.
    echo Opening Python download page...
    start https://www.python.org/downloads/
    exit /b
)

REM Remove existing virtual environment if present
echo Removing existing virtual environment...
rmdir /S /Q venv

REM Create a virtual environment to install dependencies
echo Creating virtual environment...
python -m venv venv

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip to avoid issues with older versions
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install necessary dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Install the spacy language model en_core_web_sm
echo Installing spacy language model en_core_web_sm...
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

REM Run the Python script
echo Running the pipeline script...
python 3pipeline.py

REM Deactivate virtual environment
echo Deactivating virtual environment...
deactivate

echo Done! Press any key to exit.
pause
