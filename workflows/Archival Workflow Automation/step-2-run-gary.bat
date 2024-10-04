@echo off
REM Prompt user for the base directory where scripts are located
set /p base_path="Enter the base path for the scripts (e.g., F:/NEH Grant Automated Processes/): "

REM Prompt user for the input directory where .txt files are stored
set /p input_directory="Enter the input directory path (e.g., F:/NEH Grant Automated Processes/InputTxts): "

REM Prompt user for the location of the scripts
set /p gary_primed="Enter the full path to 2-gary-primed.py: "
set /p redosubcreator="Enter the full path to redosubcreator.py: "
set /p post_good="Enter the full path to 3-POST-GOOD.py: "

REM Hardcode the OpenAI API key here
set openai_api_key=KEY

REM Generate the config.json file dynamically based on user inputs
(
echo {
echo     "base_path": "%base_path%",
echo     "input_directory": "%input_directory%",
echo     "outputs": {
echo         "2-gary-primed": "%input_directory%\\testtranscript_info.xlsx",
echo         "redosubcreator": "%input_directory%\\updated_excel_file.xlsx",
echo         "3-post-good": "%input_directory%\\output.xlsx"
echo     },
echo     "scripts": {
echo         "gary_primed": "%gary_primed%",
echo         "redosubcreator": "%redosubcreator%",
echo         "post_good": "%post_good%"
echo     },
echo     "openai_api_key": "%openai_api_key%",
echo     "retry_settings": {
echo         "delay_between_requests": 2,
echo         "max_retries": 5,
echo         "retry_delay": 3
echo     }
echo }
) > config.json

REM Run the pipeline script
python 3pipeline.py
