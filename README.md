# RAGPersonal

FastAPI-based Retrieval-Augmented Generation (RAG) service for uploading PDF resumes and asking questions about them using **OpenAI** and **Pinecone**, with simple safety guardrails and PII protection.

---

## Features

- Upload a PDF resume via `POST /upload-pdf/`.
- Index the PDF into a Pinecone vector database using OpenAI embeddings.
- Ask one or more questions via `POST /process-pdf/` and get answers grounded in the indexed PDF content.
- Guardrails in the generator so the model:
  - Uses only retrieved context.
  - Says "I don't know" when the document does not contain the answer.
  - Refuses illegal/harmful/hateful/explicit requests.
- Simple PII "middleware":
  - Emails in user queries are redacted.
  - Credit-card-like numbers are masked.
  - API keys matching `sk-********` pattern are blocked.

---

## Project Structure

- `app.py` – FastAPI entrypoint and HTTP routes.
- `core/` – configuration (loads `.env`, API keys, index name).
- `rag/` – RAG pipeline components:
  - `loader.py` – load PDF and extract text.
  - `splitter.py` – chunk the text.
  - `vector_store.py` – create / load Pinecone vector index.
  - `retriever.py` – similarity search over Pinecone.
  - `generator.py` – calls `ChatOpenAI` to generate grounded answers with guardrails + PII sanitization.
- `services/` – service layer wiring everything together (`RAGService`).
- `uploaded_files/` – PDFs uploaded at runtime.
- `docs/` – architecture docs and Mermaid diagram.

---

## Architecture

- High-level description: see `docs/architecture.md`.
- Mermaid diagram source: `docs/architecture.mmd` (can be rendered via VS Code Mermaid extension or online tools).

Typical flow:

1. Client uploads a PDF to `/upload-pdf/`.
2. Service loads and splits the PDF, embeds chunks, and upserts them into Pinecone (`PINECONE_INDEX_NAME`).
3. Client sends one or more questions to `/process-pdf/`.
4. Service retrieves top relevant chunks from Pinecone and calls OpenAI chat model to generate an answer grounded in those chunks.

---

## Requirements

- Python 3.12 (matches the provided virtual environment).
- OpenAI account + API key.
- Pinecone account + API key and an index created (or auto-created) for this app.

---

## Environment Configuration

Create a `.env` file in the project root (same folder as `app.py`):

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_index_name
```

`core/config.py` loads these values at startup and raises an error if keys are missing.

> Keep this file out of version control – **never** commit real API keys.

---

## Installation & Running (local)

1. (Optional) Create and activate a virtual environment if you are not using the existing `env/`:

   ```bash
   python -m venv env
   env\Scripts\activate   # Windows PowerShell
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI app with Uvicorn:

   ```bash
   uvicorn app:app --reload
   ```

4. Open the interactive API docs:

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## Running with Docker (optional)

If you prefer containers, you can use the provided `Dockerfile` / `Docker-compose.yaml`.

1. Build and run with Docker Compose:

   ```bash
   docker compose up --build
   ```

2. The API will be exposed on the port configured in the compose file (commonly `8000`).

Make sure your `.env` (or equivalent environment variables) are passed into the container.

---

## API Endpoints

### `GET /`

Health-check endpoint.

**Response:**

```json
{ "message": "RAG API is running!" }
```

### `POST /upload-pdf/`

Upload and index a PDF file.

- Body: multipart form with field `file` (PDF file).

**Response example:**

```json
{
  "message": "Successfully uploaded and indexed resume.pdf",
  "file_path": "uploaded_files/resume.pdf",
  "index_name": "your_index_name"
}
```

### `POST /upload-url/`

Fetch a candidate's public web page (e.g. LinkedIn profile, GitHub profile,
personal portfolio) and index its text content into Pinecone.

- Body (JSON):

```json
{ "url": "https://example.com/candidate-profile" }
```

**Response example:**

```json
{
  "message": "Successfully fetched and indexed https://example.com/candidate-profile",
  "url": "https://example.com/candidate-profile",
  "index_name": "your_index_name"
}
```

> After calling this endpoint, use `/process-pdf/` or `/agent-query/` to ask questions
> about the indexed content.

### `POST /process-pdf/`

Ask one or more questions about the indexed PDF.

- Body (JSON):

```json
[
  "What skills does this candidate have?",
  "How many years of experience?"
]
```

**Response example:**

```json
{
  "answers": [
    "The candidate has experience with Python, FastAPI, and RAG systems.",
    "They have around 3 years of professional experience."
  ]
}
```

> This endpoint assumes you have already uploaded/indexed a PDF using `/upload-pdf/`.

---

## Guardrails & PII Protection

Implemented in `rag/generator.py`:

- **Grounding rules** (system prompt):
  - Use only the retrieved `relevant_data` as knowledge.
  - If the answer is not clearly supported by `relevant_data`, respond that the document does not contain that information or that you do not know.
  - Refuse harmful, hateful, or explicit content.
  - Answer concisely and in the same language as the user query.

- **PII-like middleware on user queries**:
  - Emails → `[REDACTED_EMAIL]`.
  - Credit cards → masked, only last 4 digits kept.
  - Strings matching `sk-[a-zA-Z0-9]{32}` → request is blocked with an error.

These guardrails run before the query is sent to OpenAI, similar to a middleware layer.

---

## Model Configuration

In `rag/generator.py` the app uses `ChatOpenAI` with an explicit model:

```python
ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4.1-mini")
```

You can change `model` to any OpenAI chat model you have access to (e.g. `"gpt-4.1"`, `"gpt-4o-mini"`) depending on your cost/quality requirements.

---

## Notes

- Ensure your Pinecone index dimension and type match the embedding model you are using.
- Keep `.env` and any real credentials out of version control.
- If you change the model or embeddings, you may need to recreate/reindex your Pinecone index.
