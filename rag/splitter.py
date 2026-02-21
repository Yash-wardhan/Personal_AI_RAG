from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Split a given text into smaller chunks using RecursiveCharacterTextSplitter.

    Args:
        text (str): The input text to be split.
        chunk_size (int, optional): The maximum size of each chunk. Defaults to 1000.
        chunk_overlap (int, optional): The number of overlapping characters between chunks. Defaults to 200.

    Returns:
        list[str]: A list of text chunks.
    """
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return chunks