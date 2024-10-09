<img src="https://github.com/prys0000/congressional-portal-project/blob/main/congressthumb_home.jpg" width="11%" height="14%">

# Congressional Portal Project

## Overview

The **Congressional Portal Project** provides a repository for workflows, methodologies, instructional materials, controlled vocabularies, and more. This repository was created to house large-scale project efficiency methodologies and automated workflows and to document strategies throughout the project timeline. The project focuses on materials relating to the American Congress from the [**Carl Albert Research and Studies Center Archives**](https://www.ou.edu/carlalbertcenter/congressional-collection).

We have developed scripts and batch processes within this repository designed to automate large-scale archival workflows. The primary goal is to streamline extracting, analyzing, and enriching metadata from archival text files using Natural Language Processing (NLP) techniques and OpenAI's GPT models. This automation is crucial for efficiently managing extensive archival collections, ensuring consistent metadata quality, and enabling advanced data analysis.

### Background

- **Partnerships**: Collaborated with West Virginia University Libraries, the Robert J. Dole Institute of Politics, and the Robert C. Byrd Center for Congressional History and Education, The Dirksen Congressional Center, University of Hawai'i at Manoa, and Richard B. Russell Library for Political Research and Studies, to create the [**American Congress Digital Archives Portal**](https://congressarchives.org/)
- **Objective**: Address challenges in using congressional archives, which are large, complex, and dispersed across various institutions.
- **Focus**: Highlight materials related to American Indian sovereignty, providing insights into the struggles and achievements of American Indian communities.
- **Results**: The project began with several independent scripts handling different tasks across stages of transcription, metadata extraction, and face recognition. Over time, through multiple iterations and refinements, the workflow has evolved into a more [**streamlined and efficient pipeline**](https://github.com/prys0000/congressional-portal-project/blob/501b9ba0b95882a39753b41a3562e6434d29e5a7/workflows/README-Workflow.md). This pipeline now integrates advanced natural language and facial recognition tools, controlled lists, feedback loops, and parallel processing via MPI to enhance both accuracy and speed.

## Key Tasks

- **Develop Adaptive Learning Models**: Create and train models within a controlled environment to ensure accuracy by minimizing unreliable external information.
Automate Text Recognition and Metadata Extraction: Use NLP techniques to recognize text in archival documents and extract relevant metadata.
- **Implement Feedback Loop Mechanisms**: Establish cyclical processes that allow models to learn from each processed document, improving controlled vocabulary and identifying terminology or entities.
- **Enhance Standardization and Consistency**: Ensure all archival entries adhere to consistent standards, improving data quality and reliability across multiple projects.
- **Integrate Human-Centered Design and Linear Reciprocity Model**: Incorporate user-centric approaches and streamline data flow in the archival process.

## Automating Archival Processes

### Machine Learning Algorithms

- **Named Entity Recognition (NER)**: Identify and categorize proper nouns like people, organizations, and locations across large datasets.
- **Topic Modeling**: Uncover themes and patterns in document collections by grouping related terms and phrases.
- **Text Classification**: Connect documents to predefined terminologies and mappings based on their content.
- **Sentiment Analysis**: Assess the tone and sentiment of textual data to understand the emotional context.
- **Entity Linking**: Connect entities mentioned in the text with existing knowledge bases, enhancing accuracy.

### Feedback-Loop Controls

- **Continuous Improvement**: Use feedback loops to refine the model's understanding of text complexities, including context, sentiment, and nuanced language.
- **Contextual Analysis**: Differentiate between literal and figurative language by analyzing terms and phrases within context.
- **Verification Steps**: Implement multi-step verification to accurately identify entities, dates, and relationships.

### Controlled Vocabularies

- **Standardization**: Utilize standardized terms to ensure consistent data annotation and retrieval.
- **Enhanced Discoverability**: Cross-reference and validate data to produce accurate records, highlighting important historical contributions.

## Folders

- [**documentation-applications-list**](https://github.com/prys0000/congressional-portal-project/tree/main/documentation-applications-lists): Contains project worksheets, collection indexes, training models, and controlled vocabularies.
- [**workflows**](https://github.com/prys0000/congressional-portal-project/tree/main/workflows): Contains packaged workflows with either executable portable applications or consolidated/compiled scripts for OCR, assigning controlled metadata, and extracting specific text from OCR text.
- [**deprecated-packages**](https://github.com/prys0000/congressional-portal-project/tree/main/deprecated-packages): Contains outdated scripts and notes that have been replaced by newer versions.

## Content Overview

The Center concentrates on content related to **four curated collections, encompassing over 75,677 individual items** from the [**CAC Archives**](https://arc.ou.edu/). Additional digital files are available on our [**Digital Archives Platform**](https://oucac.access.preservica.com/).

| Collection                                                                                                                  | Type              | Topics                                                                                                                                         | Subtopics                                                                                               | Significance                                                                                                                                                                                                                                                                                                                                                                                                                                     | Extent        | Formats                                     |
| --------------------------------------------------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------- |
| Indian Self-Determination                                                                                                   | Topical           | Congress as policy-maker, Leaders and parties                                                                         | Types of decisions, Committee leadership, Policymaking in committee, Constituent communications | Congressional offices hold correspondence showcasing intricate strategies used by tribal entities and congressional members.                                                                            | 23 collections | PDF/A, PDF/E, or PDF with original file, TIFF |
| [Robert L. Owen Collection](https://arc.ou.edu/repositories/3/resources/32)                                                 | Collection-Whole  | Congress as policy-maker, Leaders and parties, Congress and the courts                                                                         | Cultural norms                                                                                          | Robert L. Owen was a member of the Cherokee Nation and represented the Five Civilized Tribes as a federal Indian agent before entering politics as a Progressive Democrat.                                                     | 199 items     | PDF/A, PDF/E, or PDF with original file, TIFF |
| [U.S. House of Representatives Offices Campaign Ads](https://arc.ou.edu/repositories/3/archival_objects/800009)             | Collection-Whole  | Leaders and parties, Elections, Congress and interest groups, Congress history - general                                                       | Leadership activities, Determinants of voting, Tactics, Electoral outcomes      | Collection of television and radio political advertisement                                                                                                  | 24,678 items  | Motion JPEG 2000, MOV, AVI                   |
| [Carl Albert Photograph Collection](https://arc.ou.edu/repositories/3/archival_objects/422780)                              | Collection-Whole  | Leaders and parties                                                                                                                            | Party leadership files                                                                                 | The personal collection of Albert’s photographs, spanning the entirety of his career.                                                                                                                                                                                                                                                                                                        | 11,000 items  | TIFF                                        |


## Acknowledgements

[Carl Albert Congressional Research and Studies Center Archives](https://www.ou.edu/carlalbertcenter/congressional-collection)

See [acknowledgments](https://github.com/prys0000/congressional-portal-project/blob/main/documentation-applications-lists/acknowledgements.md) for student staff and collaborators.

See [collaborative partners](https://github.com/prys0000/congressional-portal-project/blob/main/collaborative-partners.md) for project partners.

## Authors

[**JA Pryse**](mailto:japryse@ou.edu) - Senior Archivist III

## License

See [LICENSE](https://github.com/prys0000/congressional-portal-project/blob/main/LICENSE.md) for more information.

---

Feel free to contribute to this project by submitting issues or pull requests. Your feedback and enhancements are welcome!
