from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



def generate_response(query: str, relevant_data: list) -> str:
    """
    Generate a response to a query based on relevant data using ChatOpenAI.

    Args:
        query (str): The input query for which a response is to be generated.
        relevant_data (list): A list of relevant data to be used in generating the response.

    Returns:
        str: The generated response based on the query and relevant data.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides information based on the following relevant data: {relevant_data}"),
        ("user", "{query}")
    ])
    
    chat = ChatOpenAI()
    formatted_prompt = prompt.format(relevant_data=relevant_data, query=query)
    response = chat.invoke(formatted_prompt)
    return response.content

def generate_answer(relevant_data: list, query: str) -> str:
    """Generate a response to a query based on relevant data using ChatOpenAI.

    Args:
        relevant_data (list): A list of relevant data to be used in generating the response.
        query (str): The input query for which a response is to be generated.

    Returns:
        str: The generated response based on the query and relevant data.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides information based on the following relevant data: {relevant_data}"),
        ("user", "{query}")
    ])

    chat = ChatOpenAI()
    formatted_prompt = prompt.format(relevant_data=relevant_data, query=query)
    response = chat.invoke(formatted_prompt)
    return response.content

def generate_response(query: str, relevant_data: list) -> str:
    """Backward-compatible wrapper using the old argument order."""

    return generate_answer(relevant_data, query)