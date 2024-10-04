import subprocess
import os
import json
import sys

def main():
    # Load config from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    scripts = config['scripts']
    outputs = config['outputs']

    # Helper function to run scripts
    def run_scripts(script_path, *args):
        try:
            result = subprocess.run(['python', script_path] + list(args), capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(f"Error output: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            print(f"Error running {script_path}: {str(e)}")
            return False

    # Step 1: Run 2-gary-primed.py
    gary_primed_script = scripts['gary_primed']
    success = run_scripts(gary_primed_script)

    if success:
        print("2-gary-primed.py completed successfully.")

        # Step 2: Run redosubcreator.py
        redosubcreator_script = scripts['redosubcreator']
        redosubcreator_success = run_scripts(redosubcreator_script)

        if redosubcreator_success:
            print("redosubcreator.py completed successfully.")

            # Step 3: Run 3-POST-GOOD.py
            post_good_script = scripts['post_good']
            post_good_input = outputs['2-gary-primed']
            post_good_updated_excel = outputs['redosubcreator']
            post_good_output = outputs['3-post-good']

            post_good_success = run_scripts(
                post_good_script, post_good_input, post_good_updated_excel, post_good_output
            )

            if post_good_success:
                print(f"3-POST-GOOD.py completed successfully. Final output saved to: {post_good_output}")
            else:
                print("3-POST-GOOD.py failed.")
        else:
            print("redosubcreator.py failed. '3-POST-GOOD.py' will not be run.")
    else:
        print("2-gary-primed.py failed.")

if __name__ == "__main__":
    main()
