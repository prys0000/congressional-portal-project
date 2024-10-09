# Video Processing Pipeline Documentation

This project provides a comprehensive workflow for transcribing videos, extracting keyframes, describing those keyframes using advanced AI models, and summarizing the videos. The pipeline leverages two distinct packages with different models and utilizes Parallelization via MPI to speed up processing.

This documentation will guide you through setting up the environment, running the pipeline, and understanding each step of the process.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Get Started](#getstarted)

---

## Overview

This pipeline automates the process of:

1. **Transcribing Videos**: Utilizes **Package One** (ChatGPT-4 and Whisper) and **Package Two** (Vosk, KaldirRecognizer, Hugging Face, and EleutherAI/gpt-j-6B) to transcribe video files.
2. **Extracting Keyframes**:
   - Via speech segments.
   - At regular intervals.
3. **Describing Keyframes**: Employs advanced AI models from Package One and Package Two to generate descriptions for extracted keyframes.
4. **Summarizing Videos**: Generates summaries of videos based on transcripts and keyframe descriptions.

Additionally, the pipeline uses **Parallelization via MPI (Message Passing Interface)** to speed up processing, allowing simultaneous handling of multiple files and tasks to enhance efficiency and scalability.

---

## Prerequisites

- **Operating System**: Windows (the batch scripts are designed for Windows Command Prompt).
- **Python**: Version 3.x installed and added to your system PATH.
- **Microsoft MPI**: For parallel processing.
- **ffmpeg**: For video processing.
- **OpenAI API Key**: Access to GPT-4 with vision capabilities.
- **Additional Models and Libraries**:
  - **Package One**:
    - **ChatGPT-4**: For advanced text generation and summarization.
    - **Whisper**: OpenAI's speech recognition model.
  - **Package Two**:
    - **Vosk**: Open-source speech recognition toolkit.
    - **KaldirRecognizer**: Speech recognition library.
    - **Hugging Face Transformers**: For various NLP tasks.
    - **EleutherAI/gpt-j-6B**: Open-source GPT model for text generation.

---

## GetStarted

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/video-processing-pipeline.git
cd video-processing-pipeline
```

**Note**: This documentation assumes you have the necessary permissions and access to the required tools and APIs. Always ensure compliance with the terms of service of any third-party services used.

---

### Student Contributors (Graduate and Undergraduate)

* See [Acknowledgements](https://github.com/prys0000/congressional-portal-project/blob/8bbcd75620af3fc3a5bcf59174f8cbde14064f4f/acknowledgements.md) to view student contributors. 

### Contact

* For questions or support, please contact japryse@ou.edu. 



