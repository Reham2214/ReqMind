# ReqMind – AI-Powered Software Requirements Analysis

This project was developed as part of the **Agentic AI Bootcamp** at the **Saudi Digital Academy (SDA)**.

## Project Overview

ReqMind is a multi-agent AI system that analyzes software requirements and identifies common quality issues. It helps developers, requirements engineers, and business analysts improve requirements before development begins.

The system analyzes uploaded requirement documents and detects issues such as ambiguity, incompleteness, inconsistency, duplication, conflicts, and non-verifiable requirements. It then provides explanations, evidence, recommendations, and improved versions of the requirements.

### Analysis Workflow

**Requirement Extraction → Quality Analysis → Consistency & Conflict Analysis → Recommendations → Final Report**

## Features

* Upload requirements in **PDF, DOCX, TXT, and CSV** formats.
* Automatically extract individual software requirements.
* Analyze requirements against common quality criteria:

  * Unambiguous
  * Complete
  * Consistent
  * Verifiable

* Detect:

  * Ambiguity
  * Incompleteness
  * Duplication
  * Conflicts
  * Inconsistency
  * Non-verifiable requirements
* Generate explanations and supporting evidence for detected issues.
* Provide recommendations for improving problematic requirements.
* Generate improved versions of requirements.
* Use RAG to retrieve relevant information from a requirements knowledge base.
* Display analysis results through an interactive Streamlit interface.
* Export analysis results for further review.

## Tech Stack

### AI & Agent Framework

* **Python**
* **OpenAI**
* **LangGraph**
* **Pydantic**

### Document Processing

* **PyMuPDF** – PDF processing
* **python-docx** – DOCX processing
* **pandas** – Data processing
* **openpyxl** – Excel file processing

### RAG & NLP

* **ChromaDB** – Vector database
* **Sentence Transformers** – Text embeddings
* **scikit-learn** – Similarity and analysis

### Application

* **Streamlit** – Web interface
* **python-dotenv** – Environment variable management

## Setup & Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ReqMind
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 5. Build the RAG Knowledge Base

Before running the application, ingest the documents from the knowledge base:

```bash
.\.venv\Scripts\python.exe rag\ingest.py
```

This processes the documents in the `knowledge_base/` folder and stores their embeddings in the ChromaDB vector database.

### 6. Run the Application

```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The application will open in your browser.

## How It Works

1. **Extraction Agent** extracts individual requirements from the uploaded document.
2. **Quality Analysis Agent** checks each requirement for quality issues.
3. **Relationship Analysis Agent** compares related requirements to identify duplication, conflicts, and inconsistencies.
4. **Recommendation Agent** generates explanations, recommendations, and improved requirements.
5. **Final Report** presents the analysis and recommendations through the Streamlit interface.
