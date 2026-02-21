from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.config import OPENAI_API_KEY
import re


def _sanitize_query(query: str) -> str:
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    credit_card_pattern = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
    api_key_pattern = re.compile(r"sk-[a-zA-Z0-9]{32}")

    if api_key_pattern.search(query):
        raise ValueError("Input appears to contain an API key and was blocked.")

    query = email_pattern.sub("[REDACTED_EMAIL]", query)

    def _mask_cc(match: re.Match) -> str:
        digits = re.sub(r"[^0-9]", "", match.group(0))
        if len(digits) < 4:
            return "[MASKED_CREDIT_CARD]"
        return "*" * (len(digits) - 4) + digits[-4:]

    query = credit_card_pattern.sub(_mask_cc, query)
    return query


def generate_answer(relevant_data: list, query: str) -> str:
    """Generate a response to a query based on relevant data using ChatOpenAI.

    Args:
        relevant_data (list): A list of relevant data to be used in generating the response.
        query (str): The input query for which a response is to be generated.

    Returns:
        str: The generated response based on the query and relevant data.
    """

    safe_query = _sanitize_query(query)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful assistant that MUST follow these rules:

            1. Only use the information in `relevant_data` as your knowledge source.
            2. If the answer is not clearly supported by `relevant_data`, say you don't know
            or that the document does not contain that information.
            3. Never invent facts, names, dates, or numbers that are not in `relevant_data`.
            4. If the user asks for illegal, harmful, hateful, or explicit content,
            politely refuse to answer.
            5. Keep answers concise and in the same language as the question.

            Relevant data:
            {relevant_data}
            """,
        ),
        ("user", "{query}")
    ])

    chat = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4.1-mini",  # or "gpt-4.1", "gpt-4o-mini", etc.
    )
    formatted_prompt = prompt.format(relevant_data=relevant_data, query=safe_query)
    response = chat.invoke(formatted_prompt)
    return response.content

def generate_response(query: str, relevant_data: list) -> str:
    """Backward-compatible wrapper using the old argument order."""

    return generate_answer(relevant_data, query)