from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


def create_vector_store(chunks: list[str], index_name: str) -> PineconeVectorStore:
    """Create or update a Pinecone vector store from text chunks.

    Used when indexing a PDF at upload time.
    """

    embeddings = OpenAIEmbeddings()
    vector_store = PineconeVectorStore.from_texts(
        chunks,
        embeddings,
        index_name=index_name,
    )
    return vector_store


def get_existing_vector_store(index_name: str) -> PineconeVectorStore:
    """Connect to an existing Pinecone index for querying.

    This lets you ask questions many times after uploading once.
    """

    embeddings = OpenAIEmbeddings()
    return PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
    )