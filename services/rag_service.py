from typing import List

from rag.loader import load_pdf
from rag.splitter import split_text
from rag.vector_store import create_vector_store, get_existing_vector_store
from rag.retriever import search_relevant_data
from rag.generator import generate_answer


def run_rag_pipeline(file_path: str, query: str, index_name: str) -> str:
    """Run the complete RAG pipeline on a PDF and query.

    This function ties together loading the document, chunking, indexing,
    retrieving relevant chunks, and generating a final answer.
    """

    # Step 1: Load the PDF file and get its text
    document_text = load_pdf(file_path)

    # Step 2: Split the document into chunks
    chunks = split_text(document_text)

    # Step 3: Create a vector store from the chunks
    vector_store = create_vector_store(chunks, index_name)

    # Step 4: Search for relevant data based on the query
    relevant_data = search_relevant_data(query, vector_store)

    # Step 5: Generate an answer using the relevant data
    answer = generate_answer(relevant_data, query)

    return answer


def run_rag_pipeline_multi(queries: List[str], index_name: str) -> List[str]:
    """Answer multiple queries using the already-indexed PDF in Pinecone.

    Assumes ``index_pdf_in_pinecone`` has already been called to
    index the resume into the Pinecone index identified by ``index_name``.
    """

    vector_store = get_existing_vector_store(index_name)

    answers: List[str] = []
    for query in queries:
        relevant_data = search_relevant_data(query, vector_store)
        answer = generate_answer(relevant_data, query)
        answers.append(answer)

    return answers


class RAGService:
    """Simple service wrapper around the RAG pipeline."""

    def run_rag_pipeline(self, file_path: str, query: str, index_name: str) -> str:
        return run_rag_pipeline(file_path, query, index_name)

    def run_rag_pipeline_multi(self, queries: List[str], index_name: str) -> List[str]:
        # Use the existing Pinecone index; PDF only needed once at upload.
        return run_rag_pipeline_multi(queries, index_name)

    def index_pdf(self, file_path: str, index_name: str) -> None:
        """Load a PDF, split it, and index its chunks into a Pinecone vector store.

        This is used when you just want to upload/index a document
        without immediately asking a question.
        """

        document_text = load_pdf(file_path)
        chunks = split_text(document_text)
        # This call creates/updates the Pinecone index with the PDF chunks.
        create_vector_store(chunks, index_name)