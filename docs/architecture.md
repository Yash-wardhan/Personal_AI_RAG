# RAG Personal App Architecture

This document describes the high-level architecture of the RAGPersonal project.

## Overview

The application exposes a FastAPI backend that allows you to upload PDF resumes and then ask questions about them using a Retrieval-Augmented Generation (RAG) pipeline.

- **FastAPI app (app.py)** – defines HTTP endpoints like `/upload-pdf/` and `/process-pdf/`.
- **RAG service (services/rag_service.py)** – coordinates loading, splitting, indexing, retrieving, and answer generation.
- **Core config (core/config.py)** – loads configuration and API keys from environment variables.
- **RAG components (rag/)**:
  - **loader.py** – reads PDF files and extracts text.
  - **splitter.py** – splits raw text into smaller chunks.
  - **vector_store.py** – embeds chunks with OpenAI and stores them in a Pinecone index.
  - **retriever.py** – runs similarity search over the Pinecone index.
  - **generator.py** – calls OpenAI Chat to generate an answer from retrieved chunks.

## Data Flow

1. **Upload** – A client calls `/upload-pdf/` with a PDF.
2. **Store file** – The PDF is saved under `uploaded_files/`.
3. **Index** – The RAG service loads the PDF, splits it into chunks, embeds them with OpenAI, and upserts vectors into the Pinecone index configured by `PINECONE_INDEX_NAME`.
4. **Query** – A client calls `/process-pdf/` with one or more questions.
5. **Retrieve** – The RAG service queries the existing Pinecone index for relevant chunks.
6. **Generate** – OpenAI Chat generates an answer using the retrieved chunks and returns it via FastAPI.

## Architecture Diagram

The architecture is captured using Mermaid in [docs/architecture.mmd](docs/architecture.mmd).

You can preview it in VS Code or any Mermaid viewer. To create a PNG:

1. Open `docs/architecture.mmd`.
2. Use a Mermaid extension or online Mermaid editor.
3. Export the diagram as **PNG** and save it as `docs/architecture.png`.
