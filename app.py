from typing import List
import os

from fastapi import FastAPI
from core.config import PINECONE_INDEX_NAME
from services.rag_service import RAGService

app = FastAPI()
rag_service = RAGService()





@app.get("/")
async def root():
    """Root endpoint to confirm that the API is running.

    Returns:
        A string message confirming that the API is operational.
    """
    return {"message": "RAG API is running!"}

@app.post("/process-pdf/")
async def process_pdf(queries: List[str]):
    """Process a PDF file and answer multiple questions in one request.

    Args:
        queries: A list of questions to ask about the PDF content.
    Returns:
        A list of generated answers, one for each question in ``queries``.
    """
    index_name = PINECONE_INDEX_NAME
    answers = rag_service.run_rag_pipeline_multi(queries, index_name)
    return {"answers": answers}

#UPLOAD PDF FILES TO THE SERVER
from fastapi import File, UploadFile


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and index it into Pinecone.

    Args:
        file: The PDF file to be uploaded.
    Returns:
        A message confirming the upload and indexing location.
    """
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    index_name = PINECONE_INDEX_NAME

    # Index the uploaded PDF into Pinecone
    rag_service.index_pdf(file_location, index_name)

    return {
        "message": f"Successfully uploaded and indexed {file.filename}",
        "file_path": file_location,
        "index_name": index_name,
    }
