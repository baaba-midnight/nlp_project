# 🧩 **Ghana Legal RAG Chatbot — Backend Architecture & Methodology**

*Complete Technical Documentation*

---

## #️⃣ **1. Introduction**

This document describes the backend architecture, data pipeline, database design, and retrieval-augmented generation (RAG) workflow used to build a **Ghana Government Legal Chatbot**.
The chatbot answers questions using:

* Acts of Parliament
* Regulations
* Court Judgments
* Climate Sustainability Reports
* Other government PDFs

The system is built using:

* **FastAPI** as the backend
* **LangChain** for document loading, chunking, and pipeline orchestration
* **SentenceTransformers (MPNet)** for embeddings
* **PostgreSQL + pgvector** for vector search
* **FAISS** (optional fallback)
* **uv** environment
* **OCR** for scanned PDFs

---

## #️⃣ **2. High-Level System Architecture**

The system follows a **four-layer architecture**:

```
┌─────────────────────┐
│ 1. Data Layer       │ (PDFs: acts, judgments, regulations)
└─────────┬───────────┘
          │
┌─────────────────────┐
│ 2. Ingestion Layer  │ (PDF → text → clean → chunk → embed → DB)
└─────────┬───────────┘
          │
┌─────────────────────────────┐
│ 3. RAG Core Layer           │ (Retriever + LLM)
│  - Query embedding          │
│  - Vector search (pgvector) │
│  - Prompt construction      │
│  - LLM answer               │
└─────────┬───────────────────┘
          │
┌───────────────────────┐
│ 4. API Layer (FastAPI)│
│  - /rag/ask           │
│  - /embed/upload_pdf  │
│  - /health            │
└───────────────────────┘
```

This structure matches the requirements for:

* Fit for purpose
* Extensibility
* Climate questions
* Demonstration of technical ability
* Clear evaluation

(From project brief) 

---

## #️⃣ **3. Project Folder Structure**

```
law_rag_backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── deps.py
│   │
│   ├── api/
│   │   ├── rag_routes.py
│   │   ├── embed_routes.py
│   │   ├── health.py
│   │
│   ├── core/
│   │   ├── rag_pipeline.py
│   │   ├── retriever.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │
│   ├── services/
│   │   ├── pdf_loader.py
│   │   ├── chunker.py
│   │   ├── ingestion.py
│   │   ├── ocr_loader.py
│   │
│   ├── models/
│   │   ├── schemas.py
│   │
│   ├── utils/
│       ├── text_cleaner.py
│       ├── logging.py
│
├── vector_db/
├── data/
│   ├── acts/
│   ├── regulations/
│   ├── judgments/
│   ├── climate/
│
├── .env
└── README.md
```

---

## #️⃣ **4. Data Collection**

### **Sources**

The dataset includes:

1. **Acts of Parliament**
2. **Regulations (LIs)**
3. **Supreme Court & Court of Appeal Judgments**
4. **Climate sustainability publications**
5. **Legal PDFs from government portals**

These documents are stored under:

```
data/acts/
data/regulations/
data/judgments/
data/climate/
```

### **Why PDFs?**

* authoritative
* consistent formatting
* easy to parse
* required by project brief (government PDFs) 

---

## #️⃣ **5. Data Preprocessing Pipeline**

### **5.1 PDF → Text Extraction**

Two paths:

#### (A) Normal PDF

Using PyPDFLoader:

```python
loader = PyPDFLoader("companies_act.pdf")
docs = loader.load()
```

#### (B) Scanned PDF

Use OCR:

```python
pytesseract.image_to_string(image)
```

This enables extraction from older judgments & photocopies.

---

### **5.2 Text Cleaning**

Remove:

* headers
* footers
* page numbers
* watermarks

A regex-based cleaner is applied before chunking.

---

### **5.3 Chunking**

Legal documents need **big chunks** to preserve context.

```
chunk_size = 1000 tokens
chunk_overlap = 150 tokens
```

We use LangChain’s `RecursiveCharacterTextSplitter`.

---

### **5.4 Embedding Model**

We use:

### ⭐ `sentence-transformers/all-mpnet-base-v2`

Because:

* high accuracy
* strong legal semantic matching
* excellent on long passages
* significantly better than MiniLM for law

---

### **5.5 Embedding Storage**

Every chunk produces:

* chunk text
* 768-dim embedding
* metadata (page number, act title, source PDF)

These are stored in:

### ⬢ PostgreSQL + pgvector

**or**
FAISS (local development)

---

## #️⃣ **6. Database Design (PostgreSQL + pgvector)**

### 6.1 Install pgvector

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

### **6.2 Documents Table**

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    section TEXT,
    page INT,
    content TEXT NOT NULL,
    pdf_source TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### **6.3 Embeddings Table**

```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id),
    chunk TEXT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### **6.4 Interactions Table**

(For user queries — helps with evaluation)

```sql
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    user_query TEXT,
    retrieved_chunks TEXT,
    answer TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## #️⃣ **7. Retrieval-Augmented Generation (RAG) Pipeline**

### **7.1 Query Processing**

* Embed user query with MPNet
* Run similarity search on pgvector

### **7.2 Retrieval**

Top-k chunks (k=3–5) are selected.

### **7.3 Prompt Construction**

We use a *context-injection* prompt:

```
Use ONLY the context below to answer.

<context>
...
</context>

Question: {user_query}
```

### **7.4 Generation**

OpenAI or any LLM is used to generate the answer.

### **7.5 Output**

* answer
* optional sources
* optional top chunks

---

## #️⃣ **8. FastAPI Backend**

### **Endpoints**

#### **8.1 /rag/ask**

Handles questions:

```json
POST /rag/ask
{
  "query": "What does the Companies Act say about auditor responsibilities?"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [...]
}
```

---

#### **8.2 /embed/upload_pdf**

Add new PDFs → ingestion pipeline → database updated.
This proves **extensibility**, which is required. 

---

#### **8.3 /health**

Service check.

---

## #️⃣ **9. Tools & Environment Setup (uv)**

### Create environment

```bash
uv venv
```

### Install packages

```bash
uv add fastapi uvicorn langchain langchain-community
uv add sentence-transformers faiss-cpu openai
uv add pypdf beautifulsoup4 lxml python-multipart
uv add psycopg2-binary
uv add unstructured pytesseract pillow
uv add python-dotenv
```

### Run server

```bash
uv run uvicorn app.main:app --reload
```

---

## #️⃣ **10. Evaluation Strategy**

### **10.1 Accuracy Testing**

Ask:

* legal questions
* climate questions
* procedural questions
* definition questions

Validate against source PDFs.

---

### **10.2 Extensibility Test**

Upload a *new Act* during demo → system re-indexes → chatbot can use it.

---

### **10.3 Performance**

Measure:

* retrieval time
* embedding time
* DB query latency

---

## #️⃣ **11. Conclusion**

This backend architecture provides:

* a robust Ghana-focused RAG system
* vector search that scales
* a clean ingestion pipeline
* extensibility (required by the project)
* ability to answer legal + climate questions
* a professional FastAPI backend
* OCR support for older government documents

This structure is fully defendable in an interview and aligns directly with the project’s evaluation criteria.
