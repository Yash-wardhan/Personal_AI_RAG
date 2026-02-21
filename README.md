# RAGPersonal

A small FastAPI-based Retrieval-Augmented Generation (RAG) app for uploading PDF resumes and asking questions about them using OpenAI and Pinecone.

## Features

- Upload a PDF resume via `/upload-pdf/`.
- Index the document into a Pinecone vector database using OpenAI embeddings.
- Ask one or more questions via `/process-pdf/` and get AI-generated answers grounded in the indexed PDF content.

## Project Structure

- `app.py` – FastAPI entrypoint and HTTP routes.
- `core/` – configuration (API keys, index name).
- `rag/` – RAG pipeline components (loader, splitter, vector store, retriever, generator).
- `services/` – service layer wiring everything together.
- `uploaded_files/` – PDFs uploaded at runtime.
- `docs/` – documentation and architecture diagrams.

## Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed description and [docs/architecture.mmd](docs/architecture.mmd) for the Mermaid source of the architecture diagram.

You can export a PNG diagram from `docs/architecture.mmd` and save it as `docs/architecture.png`.

## Setup

1. Create and activate a virtual environment (already present as `env/` in this project).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables in `.env`:

   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME` (e.g. a dense index like `rag-dense`).

4. Run the FastAPI app (for example using `uvicorn`):

   ```bash
   uvicorn app:app --reload
   ```

5. Open the interactive docs at `http://localhost:8000/docs`.

## Usage

1. **Upload a PDF**

   Use the `/upload-pdf/` endpoint to upload your resume. This indexes the document into Pinecone.

2. **Ask questions**

   Call `/process-pdf/` with a list of questions in the request body. The app queries Pinecone and uses OpenAI Chat to answer based on your resume.

## Notes

- Make sure your Pinecone index type (dense, correct dimension) matches the embedding model used by `OpenAIEmbeddings`.
- API keys in `.env` should be kept secret (do not commit them to version control).
