# RAG Document Assistant

A local Retrieval-Augmented Generation (RAG) application that allows users to upload PDF or TXT documents, ask questions about their content, and inspect the retrieved evidence used to generate answers.

## Features

- Upload PDF and TXT documents through a web interface.
- Extract text, clean it, and divide it into chunks.
- Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
- Retrieve relevant chunks using cosine similarity.
- Generate answers locally using Ollama and `llama3.2:3b`.
- Display retrieved evidence and similarity scores.
- Use a Flask backend with an HTML, CSS, and JavaScript frontend.

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Embeddings:** Sentence Transformers
- **Similarity search:** NumPy and cosine similarity
- **Local LLM:** Ollama (`llama3.2:3b`)
- **PDF extraction:** pypdf

## Architecture

1. The user uploads a PDF or TXT document.
2. The backend extracts and cleans the text.
3. The text is split into chunks with overlap.
4. The embedding model generates vector representations of the chunks.
5. A user question is embedded and compared with the document chunks.
6. The top three relevant chunks are sent to the local LLM as context.
7. Ollama generates an answer, and the UI displays it with retrieved evidence.

## Prerequisites

- Python 3.11 or another Python version compatible with the installed dependencies.
- Ollama installed and running locally.
- Git.

## Setup

Clone the repository and enter the project directory:

```bash
git clone <YOUR_REPOSITORY_URL>
cd RAG-resume
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install the local LLM:

```powershell
ollama pull llama3.2:3b
```

Start Ollama, then launch the Flask application:

```powershell
python backend/app.py
```

Open http://127.0.0.1:5000 in your browser.

The embedding model may be downloaded the first time the application starts.

## Project Structure

```text
RAG-resume/
├── backend/
│   └── app.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── documents/
├── compare_extraction.py
├── inspect_resume.py
├── rag_qa.py
├── semantic_search.py
├── text_cleaner.py
├── text_chunker.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Current Limitations

- Only one active document is held in server memory at a time.
- Uploaded documents and embeddings are not persisted between server restarts.
- Scanned PDFs requiring OCR are not supported yet.
- Retrieval uses cosine similarity and a fixed top-three chunk selection.
- The application is a local learning prototype, not a production multi-user service.

## Future Improvements

- Improve retrieval quality and evaluate retrieval metrics.
- Add OCR support for scanned PDFs.
- Add persistent document storage and a vector database.
- Add automated tests and document-level isolation for multiple users.
- Improve prompt-injection resistance and answer evaluation.

## Privacy

Do not commit personal resumes, confidential documents, API keys, credentials, or other sensitive data. Uploaded documents should remain local unless you explicitly choose to share them.
