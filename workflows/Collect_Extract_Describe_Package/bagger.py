#The Bagger application was created for the U.S. Library of Congress as a tool to produce a package of data files according to the BagIt specification http://tools.ietf.org/html/draft-kunze-bagit
#Use the script below to auomate bagging or download from the website above 
 ---- ----- ----

import json
import subprocess

def generate_bag_info(config):
    """
    Generate bag-info.txt content based on the provided configuration.

    Args:
    - config (dict): JSON configuration for customizing bag contents.

    Returns:
    - str: Content of the bag-info.txt file.
    """
    bag_info = []

    for field, settings in config.items():
        line = f"{field}:"

        if settings.get("fieldRequired", False):
            line += " REQUIRED"
        else:
            line += " OPTIONAL"

        if "requiredValue" in settings:
            line += f" '{settings['requiredValue']}'"

        if "defaultValue" in settings:
            line += f" {settings['defaultValue']}"

        if "valueList" in settings:
            line += f" {', '.join(settings['valueList'])}"

        bag_info.append(line)

    return "\n".join(bag_info)

def bag_files(bagger_path, source_directory, output_directory, bag_info_content=None):
    """
    Bag files using Library of Congress Bagger program.

    Args:
    - bagger_path (str): Path to the Bagger executable.
    - source_directory (str): Path to the directory containing files to be bagged.
    - output_directory (str): Path to the directory where the bag should be created.
    - bag_info_content (str): Content for bag-info.txt file.

    Returns:
    - bool: True if bagging is successful, False otherwise.
    """
    # Construct the command to run Bagger
    command = [
        "java", "-jar", bagger_path,
        "bag",
        "--dir", source_directory,
        "--output", output_directory
    ]

    if bag_info_content:
        bag_info_file = os.path.join(output_directory, "bag-info.txt")
        with open(bag_info_file, "w") as f:
            f.write(bag_info_content)
        command.extend(["--bag-info", bag_info_file])

    try:
        # Execute the command
        subprocess.run(command, check=True)
        print("Bagging completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Path to the Bagger executable
    bagger_path = "/path/to/bagger/bagger-cli.jar"

    # Source directory containing files to be bagged
    source_directory = "/path/to/source/directory" #ADD YOUR PATH TO FILES

    # Output directory where the bag will be created
    output_directory = "/path/to/output/directory" #ADD PATH TO OUPUT BAGS

    # JSON configuration for customizing bag contents #CUSTOMIZE YOUR BAG HERE
    bag_config = {
        "Contact-Name": {"fieldRequired": True, "requiredValue": "John Doe"},
        "Contact-Email": {"fieldRequired": True, "requiredValue": "john.doe@example.com"},
        "Organization-Address": {"fieldRequired": False, "defaultValue": "123 Main St"},
        "Source-Organization": {"fieldRequired": True, "valueList": ["Library", "Archive"]}
    }

    # Generate bag-info.txt content
    bag_info_content = generate_bag_info(bag_config)

    # Bag the files
    success = bag_files(bagger_path, source_directory, output_directory, bag_info_content)

    if success:
        print("Bagging process completed successfully.")
    else:
        print("Bagging process failed.")
