# AI Technical Interviewer: An Agentic System for Automated Assessment

## Project Overview

The **AI Technical Interviewer** is a state-aware, agentic application designed to simulate real-world technical interviews. Built using **LangGraph** and **Groq (Llama-3)**, the system orchestrates multiple AI agents to analyze resumes, generate context-aware technical questions, evaluate candidate responses in real-time, and provide vocal feedback.

Unlike standard chatbots, this system maintains a persistent conversation state, allowing it to ask follow-up questions based on the depth of a candidate's answer. It is optimized for low-latency performance (<1.5s response time) and includes a real-time metric dashboard for token usage and operational cost monitoring.

## Key Features

* **Resume-Driven Context:** Automatically parses PDF resumes using `pypdf` to extract skills, experience level, and domain expertise, tailoring the interview strategy accordingly.
* **Multi-Agent Architecture:**
    * **Interviewer Agent:** Formulates natural, spoken-style questions based on the current interview stage.
    * **Grader Agent:** A "Human-in-the-loop" simulator that fact-checks answers against technical ground truths, assigning status (Correct/Partially Correct/Incorrect) and determining if a follow-up question is required.
* **Low-Latency Inference:** Powered by **Groq API** (Llama-3-70b), achieving inference speeds significantly faster than traditional models, ensuring a fluid conversational experience.
* **State Management:** Utilizes **LangGraph** to handle the cyclical workflow of questioning, waiting for user input, grading, and responding.
* **Voice Interface:** Integrated Text-to-Speech (gTTS) to simulate a live voice call environment.
* **Performance Telemetry:** Displays real-time system metrics including average latency per turn and total token consumption for cost estimation.
* **Automated Reporting:** Generates a comprehensive PDF report at the end of the session, summarizing performance, question difficulty, and detailed feedback.

## Technical Architecture

The application follows a modular architecture orchestrated by a central State Graph.

1.  **Input Layer:** Streamlit interface captures user inputs (Resume, Audio/Text answers).
2.  **Processing Layer (LangGraph):**
    * **ProfileAnalyzer:** Extracts metadata from the resume.
    * **QuestionGenerator:** Creates a dynamic 5-question strategy using a randomized seed to prevent repetition.
    * **InterviewerNode:** Manages the conversation flow.
    * **GraderNode:** Performs semantic evaluation of the user's response.
3.  **Inference Layer:** Groq API serves as the LLM backbone for high-speed text generation.
4.  **Output Layer:** Returns text responses, synthesized audio, and updates the session state database.

## Tech Stack

* **Language:** Python 3.10+
* **Orchestration:** LangGraph, LangChain
* **Inference Engine:** Groq (Llama-3-70b-Versatile)
* **Frontend:** Streamlit
* **Data Processing:** pypdf (PDF parsing), fpdf (Report generation)
* **Audio:** gTTS (Google Text-to-Speech)
* **State Management:** Streamlit Session State & LangGraph StateDict

## Installation & Setup

### Prerequisites
* Python 3.9 or higher
* A Groq API Key (Free tier available at console.groq.com)

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
