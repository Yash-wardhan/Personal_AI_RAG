#Search relevant data
 
from langchain_community.vectorstores import Pinecone


def search_relevant_data(query: str, vector_store: Pinecone, top_k: int = 5) -> list:
    """Search for relevant data in an existing Pinecone vector store.

    Args:
        query: The search query.
        vector_store: An initialised Pinecone vector store to search in.
        top_k: The number of top results to return. Defaults to 5.

    Returns:
        A list of relevant data retrieved from the vector store.
    """

    return vector_store.similarity_search(query, k=top_k)