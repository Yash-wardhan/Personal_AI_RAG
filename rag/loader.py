from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path: str) -> str:
    """Load a PDF file and return its full text content.

    Args:
        file_path: The path to the PDF file.

    Returns:
        A single string containing the concatenated text of all pages.
    """

    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return "\n".join(page.page_content for page in pages)