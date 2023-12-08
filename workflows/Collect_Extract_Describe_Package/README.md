## Collect_Extract_Describe_Package

This package is designed to process large-scale collections of text and photographic materials, analyze extract pre-defined information from trained models, generate summaries and specified metadata from their contents. It uses various controlled and customizable libraries and APIs, for text generation, named entity recognition, and project specific data. 

**Key functionalities:**

* **Libraries and Setup:**
    * Script #1, ${\color{red}gary.py}$ imports necessary libraries such as spaCy, pandas, and others. It also sets up API keys, directories, and global variables.

* **Preprocessing and Post-processing Functions:**
    * Two functions, preprocess_text and postprocess_text, handle text preprocessing and post-processing tasks, such as removing special characters and cleaning up the text.

* **Data Storage Lists:**
    * ${\color{red}gary.py}$ initializes several empty lists to store data extracted from the text files, including filenames, summaries, congress, creators, recipients, subjects, tribes, dates, named entities, states, policies, parties, and tribal organizations.

* **Text Processing Functions:**
    * There are various functions to process and extract information from the text files. These functions handle tasks like extracting dates, named entities, tribes, states, generate titles and summaries, identify the nature of the documents or photographs (constituent corespondence, form, memo, telegram, published work, as well as the tone).

* **DataFrame Creation:**
    * The collected data is organized into a pandas DataFrame for easy manipulation and analysis. Additional information, such as Congress based on dates, is also included.

* **Quality Controll and Error Detection:**
    * After the DataFrame is created, ${\color{red}gary.py}$ validates each component for accuracy or potential errors with spelling, word organization, dates and years and related legislation and congressional date ranges, and validates tribal affiliation accuracy (project specific metric).

* **Export to Excel:**
    * The DataFrame is saved as an Excel file for further analysis or reporting. (*note: if conversion of file typoes are specified those items are also printed to the directory*)

**Transform data for ArchivesSpace, Preservica, and NEH Congressonal Portal:** Script #2, ${\color{green}helen.py}$ is designed to streamline a multi-step process that involves reading data from an Excel sheet, performing various checks and validations, highlighting potential errors, and ultimately transforming the data into platform-specific bulk uploads.

* **Data Retrieval from Excel Sheet:**

    * ${\color{green}helen.py}$ begins by reading data from an Excel sheet. This data likely contains information related to archival resources, possibly in tabular format.

* **Data Validation and Review:**

    * After retrieving the data, ${\color{green}helen.py}$ performs a series of validation checks to ensure data accuracy and consistency. It will check for missing or incorrect entries, missing metadata or inconsistent date formats.

* **Spell Check:**

    * ${\color{green}helen.py}$ conducts a spell check to identify and highlight potential spelling errors in the data. This ensures that the textual content is free from typos or misspelled words.

* **Error Identification:**

    * ${\color{green}helen.py}$ identifies and highlights other potential errors or inconsistencies within the data. These errors could be related to metadata, formatting, or any other relevant criteria.

* **Data Transformation:**

    * Once the data has been validated and potential errors are addressed, ${\color{green}helen.py}$ proceeds to transform the data.
    * Transformation involves converting the data into a format that is compatible with various archival platforms.
    * This may include structuring the data hierarchically, generating XML files, and preparing files for upload.

* **Platform-Specific Bulk Uploads:**

    * The transformed data is tailored to meet the requirements of specific archival platforms.
    * Each platform may have its own format and structure for data uploads, and the script ensures compliance.

* **Resource Generation:**

    * ${\color{green}helen.py}$ generates multiple resources, such as folders, files, or items, based on the transformed data.
    * Original items in various file formats (e.g., .pdf, .txt, .doc, .jpg, .tif, .png) are included.

* **XML Creation:**

    * For each folder or item, ${\color{green}helen.py}$ generates XML files that contain metadata and other necessary information for archival purposes.
    * These XML files serve as structured representations of the resources.

* **Hierarchy Maintenance:**

    * ${\color{green}helen.py}$ maintains the hierarchical structure of the data, ensuring that the relationships between items, folders, and collections are preserved.

* **Preservation and Compression:**

    * Preservation folders are created to store the archival resources in their original state, along with relevant metadata.
    * These preservation folders are typically "bagged" according to archival standards to ensure long-term data preservation.

* **Queuing for Long-Term Storage:**

    * Finally, ${\color{green}helen.py}$ queues the preservation folders for long-term storage, ensuring that the archival resources are securely stored and accessible for the future.

* **Customizability:**
    * One of the key features of the script is its ***customizability***.
    * Users can configure various parameters and settings to adapt the data transformation and upload process to their specific needs and the requirements of different archival platforms.

