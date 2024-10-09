# Workflow README

This folder contains information and complete workflow packages, topic and training models, and a basic student information guide. 

## **Topics and Keywords** columns/lists were compiled from:  

* [The Congress Project, Data and Links](https://www.thecongressproject.com/data-and-links/#Important%20Legislation) 
* [The-Policy-Agendas-Project](https://liberalarts.utexas.edu/government/news/feature-archive/the-policy-agendas-project.html)
* [Congress.gov, Policy Area Term Vocabulary](https://www.congress.gov/browse/policyarea)
* [Codebook for U.S. Senate Returns 1976–2018](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PEJ5QU)
* [ICPSR Roster of United States Congressional Officeholders and Biographical Characteristics of Members of the United States Congress](https://www.icpsr.umich.edu/web/ICPSR/series/156)
* [Federally Recognized Tribes - US Department of Interior, Indian Affairs](https://www.bia.gov/service/tribal-leaders-directory/federally-recognized-tribes)

## **Scripts and Files:**

*Note: all scripts in this folder are ***templates*** and must be edited for each project. You can use these as a starting place to build a tailored project deployment.* 

## Evolution of the Workflow: From Multiple Scripts to One Parallelized Pipeline

The project began with several independent scripts handling different tasks across stages of transcription, metadata extraction, and face recognition. Over time, through multiple iterations and refinements, the workflow has evolved into a more streamlined and efficient pipeline. This pipeline now integrates advanced natural language and facial recognition tools, controlled lists, feedback loops, and parallel processing via MPI to enhance accuracy and speed.

## Initial Approach (Multi-Staged Workflow):

1. **Text Extraction from PDFs**:
   - Early scripts used OCR (PyTesseract) to extract text from PDFs by converting pages to images with PyMuPDF. This process saved the text as `.txt` files for further analysis but required manual oversight and was relatively slow for bulk processing.

2. **AWS for PDF Text Recognition**:
   - Integrated AWS to process PDF files directly from S3 buckets, automating text extraction and generating Excel reports with technical data such as file size and page dimensions.

3. **Summarization and Named Entity Recognition**:
   - Scripts leveraged **[OpenAI (paid version)](https://openai.com/)** or **Vosk, KaldiRecognizer (free version)** to generate summaries and titles for text files, while spaCy was used for Named Entity Recognition (NER) to identify and extract people, places, and organizations. Subjects, policies, and affiliations were assigned using predefined mappings and keyword lists, but this process needed further refinement to handle more complex relationships.

4. **Excel Report Generation**:
   - Extracted metadata, summaries, and identified entities were compiled into Excel reports. This made the data more accessible but required multiple steps to produce a cohesive output.

## Refinements and Iterations:

Over time, **controlled lists and dictionaries** were introduced to better map keywords and entities, making the recognition process more accurate. The mappings evolved to capture complex entity relationships such as tribal leaders, historical figures, and document contexts, enabling more sophisticated text learning.

Refined dictionaries improved the system's natural language understanding, allowing it to identify better-nuanced connections between subjects, people, and events across documents. This also extended to facial recognition, where controlled lists of faces were integrated into feedback loops to enhance the accuracy of bulk face recognition in images, allowing the system to learn from corrections and improve iteratively.

## Current Approach (One Integrated, Parallelized Pipeline):

The system has now evolved into a **single automated pipeline**, combining all previous stages into a cohesive, faster process that integrates natural language tools, complex entity recognition, feedback loops, and parallel processing via MPI for continuous improvement and speed enhancement.

### 1. Modular Configuration:

- The pipeline is driven by a `config.json` file, which defines input directories, script paths, and output files. This setup enables flexibility and easy modifications without changing the main code, making it adaptable to different projects or datasets.

### 2. Parallel File Processing via MPI:

- **Parallelization with MPI**:
  - To handle large volumes of data efficiently, the pipeline now utilizes **Parallelization via MPI (Message Passing Interface)**. MPI allows the distribution of tasks across multiple processors or cores, enabling simultaneous processing of multiple files.
  - Each `.txt` file is processed in parallel, running through steps like summarization, entity recognition, controlled list mapping, and metadata extraction.
  - This approach significantly reduces processing time and enhances the system's scalability.

### 3. Integrated Feedback Loops:

- **Continuous Learning**:
  - Facial recognition and contextual relationships benefit from integrated feedback loops that update and correct errors during processing.
  - The system learns from each iteration, improving its efficiency in recognizing faces and understanding text context in future runs.

### 4. Error Handling and Logging:

- Improved error handling ensures that any issues encountered at any stage do not disrupt the entire pipeline. Logs are generated to provide clear insights into where problems occur, facilitating easier debugging and correction.

## Implementation of Parallelization via MPI:

### Why MPI?

- **Standardization and Portability**:
  - MPI is a standardized, portable message-passing system for parallel computing architectures.
- **Efficiency**:
  - It optimizes available computational resources, reducing processing time for large datasets.
- **Scalability**:
  - Easily scales with the addition of more processors or computing nodes.

### How It's Integrated:

- **Distributed Processing**:
  - The pipeline scripts are structured as MPI processes, distributing tasks like text extraction, summarization, and entity recognition among multiple processors.
- **Synchronization**:
  - MPI ensures proper communication and synchronization between processes, maintaining data integrity and consistency.
- **Resource Management**:
  - Efficiently manages memory and CPU usage across multiple cores or nodes, preventing bottlenecks.

## Future Enhancements:

### Further Optimization of Parallel Processing:

- **Load Balancing**:
  - Fine-tuning the MPI implementation to ensure an even distribution of tasks, minimizing idle time for any processor.
- **Hybrid Parallelization**:
  - Combining MPI with multi-threading (e.g., OpenMP) for tasks that benefit from shared-memory parallelism within a node.

### Automated Testing:

- Developing unit tests for each pipeline component will ensure the system works as intended across each stage, improving overall reliability.

### Advanced Summarization and Topic Modeling:

- Fine-tuning parameters to generate more nuanced summaries and improve the automatic identification of topics in audiovisual transcriptions.

### Customizable Summarization Parameters:

- Refining OpenAI API parameters (e.g., token length, temperature) to enhance the quality of the summaries and titles generated by the pipeline.

## Benefits Achieved:

- **Significant Speed Improvements**:
  - Parallel processing via MPI has drastically reduced the time required to process large datasets.
- **Enhanced Accuracy**:
  - Integrated feedback loops and controlled vocabularies improve entity recognition and metadata extraction precision.
- **Scalability**:
  - The system can handle increasing volumes of data without performance degradation.
- **Resource Optimization**:
  - Efficient utilization of computational resources leads to cost savings and better performance.

## Conclusion:

This integrated, parallelized, and feedback-driven pipeline significantly advances handling bulk transcriptions, entity recognition, and metadata generation. The system achieves higher processing speeds and scalability by incorporating parallelization via MPI. Continuous learning through feedback loops ensures ongoing improvement in accuracy and efficiency. The result is a faster, more intelligent system capable of processing complex archival materials at scale, greatly benefiting large-scale archival projects.
