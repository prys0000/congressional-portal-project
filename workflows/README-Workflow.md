## Workflow README

This folder contains information and full workflow packages, topic and training models, as well as a basic student information guide. 

**Document.md files labeled 1-6** are basic documentation on the project, standard workflows, and other information about the project.

**CAC_NER_trainingmodel.csv** was created to help standardize metadata and provide automatic term/text selections for scripts.

**CAC_TOPICS_trainingmodel.csv** was created to categorize and standardize topics related to political science. 

**Topics and Keywords** columns/lists were compiled from:  

* [The Congress Project, Data and Links](https://www.thecongressproject.com/data-and-links/#Important%20Legislation) 
* [The-Policy-Agendas-Project](https://liberalarts.utexas.edu/government/news/feature-archive/the-policy-agendas-project.html)
* [Congress.gov, Policy Area Term Vocabulary](https://www.congress.gov/browse/policyarea)
* [Codebook for U.S. Senate Returns 1976–2018](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PEJ5QU)
* {ICPSR Roster of United States Congressional Officeholders and Biographical Characteristics of Members of the United States Congress](https://www.icpsr.umich.edu/web/ICPSR/series/156)
* [Federally Recognized Tribes - US Department of Interior, Indian Affairs](https://www.bia.gov/service/tribal-leaders-directory/federally-recognized-tribes)

All scripts in this folder are ***templates*** and need to be adjusted for each project. Use these as a starting place to build a tailored project deployment. 

**AV_Transcription_Package** contains:

* AV_Transcript.py and notes files -  basic scripts for transcribing audio and video files
* AV_Transcript-app.py and notes files - full script to create a portable 'app' or application to be used on multiple workstations without installing python or python interpreter. 
* AV-enhanced-topic.py - script to identify and assign topics from a trained topic model, like the CAC_TOPICS_trainingmodel.csv mentioned above.

**Extract_Package** contains:

* This folder contains a script that was designed to read text, filter common words/phrases, assign pre-defined text, check spelling and grammar and save metadata to a structured excel file for easy manipulation of data. 

**OCR_Package** contains:

* This folder contains the entire downloadable package for a portable OCR application that can be used on multiple student workstations as a part of the day-to-day routine to read pdf or text files and extract text either (1) into a text file or (2) into an excel file with file names. 
