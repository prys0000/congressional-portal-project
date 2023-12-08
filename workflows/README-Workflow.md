# Workflow README

This folder contains information and full workflow packages, topic and training models, as well as a basic student information guide. 

## **Topics and Keywords** columns/lists were compiled from:  

* [The Congress Project, Data and Links](https://www.thecongressproject.com/data-and-links/#Important%20Legislation) 
* [The-Policy-Agendas-Project](https://liberalarts.utexas.edu/government/news/feature-archive/the-policy-agendas-project.html)
* [Congress.gov, Policy Area Term Vocabulary](https://www.congress.gov/browse/policyarea)
* [Codebook for U.S. Senate Returns 1976–2018](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PEJ5QU)
* [ICPSR Roster of United States Congressional Officeholders and Biographical Characteristics of Members of the United States Congress](https://www.icpsr.umich.edu/web/ICPSR/series/156)
* [Federally Recognized Tribes - US Department of Interior, Indian Affairs](https://www.bia.gov/service/tribal-leaders-directory/federally-recognized-tribes)

## **Scripts and Files:**

*Note: all scripts in this folder are ***templates*** and need to be edited for each project. Use these as a starting place to build a tailored project deployment.* 

[**Collect_Extract_Describe_Package:**](https://github.com/prys0000/congressional-portal-project/tree/60a05a722da22408062d1dc12e3ea30630c4f913/workflows/Collect_Extract_Describe_Package) contains:
* ${\color{red}gary.py}$ - script to analyze text, images, OCR, summarize, create title, assign multiple pre-designed and pre-trained topics/subjects.
* ${\color{green}helen.py}$ - script to validate and quality check reults from gary.py as well as create iterations of files and long-term storage bagging.

[**AV_Transcription_Package**](https://github.com/prys0000/congressional-portal-project/tree/60a05a722da22408062d1dc12e3ea30630c4f913/workflows/AV_Transcriptions_Package) contains:

* ${\color{blue}allan.py}$ and notes files - full script to create a portable 'app' or application to be used on multiple workstations without installing python or python interpreter.
* ${\color{teal}allanjr.py}$ and notes files -  basic scripts for transcribing audio and video files
* ${\color{orange}beth.py}$ - script to identify and assign topics from a trained topic model, like the CAC_TOPICS_trainingmodel.csv mentioned above.

[**Face_Recogition_Package**](https://github.com/prys0000/congressional-portal-project/tree/60a05a722da22408062d1dc12e3ea30630c4f913/workflows/Face_Recognition_Package) contains:

* This folder contains dave.py, and workflow notes for detecting and identifying faces of political figures in photographic images. 

***Depreciated (older) packages for review:***

[**OCR_Package**](https://github.com/prys0000/congressional-portal-project/tree/60a05a722da22408062d1dc12e3ea30630c4f913/depreciated-packages/OCR_package) contains:

* This folder contains the entire downloadable package for a portable OCR application that can be used on multiple student workstations as a part of the day-to-day routine to read pdf or text files and extract text either (1) into a text file or (2) into an excel file with file names. 

[**Extract_Package**](https://github.com/prys0000/congressional-portal-project/tree/60a05a722da22408062d1dc12e3ea30630c4f913/depreciated-packages/Extract_Package) contains:

* This folder contains a script that was designed to read text, filter common words/phrases, assign pre-defined text, check spelling and grammar and save metadata to a structured excel file for easy manipulation of data.


