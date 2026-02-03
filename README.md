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
```
### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.Configuration
Create a .env file in the root directory and add your API credentials:
```bash
GROQ_API_KEY=gsk_your_api_key_here
```

### 5.Run the Application
```bash
streamlit run main.py
```
## Usage Guide

1. **Upload Resume:** On the sidebar, upload a candidate's resume (PDF format).
2. **Configure Role:** Select the target role (e.g., AI Engineer, SDE) and experience level.
3. **Start Interview:** Click "Start Interview" to initialize the agent workflow.
4. **Interaction:**
    * The system will audibly ask the first question.
    * Type your answer in the chat box.
    * The Grader Agent will evaluate the response silently.
    * The Interviewer Agent will either ask a follow-up or move to the next topic.
5. **Report:** Upon completion (5 questions), download the detailed PDF feedback report.

## Metric Tracking

The application dashboard includes a **Live Metrics** section designed to demonstrate system optimization:

* **Tokens:** Tracks total context window usage (Input + Output tokens) to estimate API costs.
* **Avg Latency:** Monitors the "Time-to-First-Token" ensuring the system remains responsive (<2s).

  This project is done for educational purposes only


