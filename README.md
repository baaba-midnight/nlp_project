# 🧩 Ghana Legal RAG Chatbot

A production-ready retrieval-augmented generation (RAG) system for answering questions about Ghanaian legal documents using vector search and LLMs.

**Backend:** FastAPI + PostgreSQL + pgvector  
**Frontend:** Vanilla HTML/CSS/JavaScript  

---

## Prerequisites

### Install uv (Python Package Manager)

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative (using pip):**

```bash
pip install uv
```

---

## Quick Start

### Backend Setup

1. **Navigate to backend**
  
   ```bash
   cd backend
   ```

2. **Create environment** (using `uv`)

   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   cd backend
   uv pip install -r requirements.txt
   ```

4. **Configure .env**

   ```bash
   # backend/.env
   DATABASE_URL=postgresql://user:password@localhost:5432/ghana_rag
   OPENAI_API_KEY=sk-...
   VECTOR_STORE=pgvector  # or 'faiss' for development
   ```

5. **Start server**

   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

   ✅ Server running: `http://localhost:8000/docs`

---

### Frontend Setup

1. **Update API URL** (if needed)

   ```javascript
   // frontend/app.js
   const API_BASE_URL = 'http://localhost:8000'; // Change if backend port differs
   ```

2. **Serve frontend** (keep backend running in another terminal)

   ```bash
   cd frontend
   python -m http.server 8080
   ```

3. **Open browser**

   ```bash
   http://localhost:8080
   ```

---

## 📁 Project Structure

```
nlp_project/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── upload.py       (URL & file ingestion)
│   │   │   └── rag_ask.py          (Query endpoint)
│   │   │   └── conversations.py          (Conversation and Message Endpoint)
│   │   │   └── translate.py          (Translate English-to-Twi endpoint)
│   │   │   └── upload.py          (Upload endpoint)
│   │   ├── services/
│   │   │   ├── loaders/        (PDF, OCR, Hybrid)
│   │   │   ├── scrapers/       (Web scraper)
│   │   │   └── ingestor.py     (Chunking & embedding)
│   │   └── core/               (RAG pipeline, retriever)
│   └── .env
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
└── data/                       (Sample PDFs)
```

---

## 🔧 Key Features

| Feature | Details |
|---------|---------|
| **Multiple Ingestion** | Upload PDFs, scrape URLs, detect URLs in text files |
| **Scanned PDFs** | Hybrid loader falls back to Tesseract OCR |
| **Vector Search** | PostgreSQL + pgvector for semantic similarity |
| **Domain Optimized** | MPNet embeddings trained on legal/technical text |
| **RAG Pipeline** | Retrieval → Context assembly → LLM generation |
| **Extensible** | Add new documents dynamically without retraining |

---

## 🛠 Configuration

### Backend (.env)

Setup the following enviornment variables before activating the backend

```bash
user= 
password=
host=
port=5432
dbname=postgres
supabase_url=
supabase_key=
colab_url = 
```

### Frontend (app.js)

```javascript
const API_BASE_URL = 'http://localhost:8000';
const CHUNK_SIZE_MB = 10;
```

---

### Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 8000 in use** | Change port: `uvicorn app.main:app --port 8001` + update `API_BASE_URL` |
| **Connection refused** | Verify backend is running at `http://localhost:8000/docs` |
| **CORS errors** | Use local server (`python -m http.server`), not `file://` |
| **DB connection failed** | Check `DATABASE_URL` in `.env` and PostgreSQL is running |
| **OCR not working** | Install Tesseract: `brew install tesseract` (Mac) or `apt install tesseract-ocr` (Linux) |

---

## 📚 Technical Stack

- **Framework:** FastAPI + Uvicorn
- **Database:** PostgreSQL + pgvector (supabase)
- **Embeddings:** sentence-transformers/all-mpnet-base-v2
- **LLM:** OpenAI GPT (configurable)
- **PDF Processing:** pypdf + Tesseract OCR
- **Web Scraping:** BeautifulSoup4 + requests
- **Frontend:** Vanilla JS (no frameworks)

---

## 📖 Architecture Overview

**See:** [`docs/ARCHITECTURE.md`](./docs/system_architecture.plantUML)
