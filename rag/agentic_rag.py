from typing import Dict, Any

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from core.config import OPENAI_API_KEY, PINECONE_INDEX_NAME
from rag.vector_store import get_existing_vector_store
from rag.retriever import search_relevant_data
from rag.generator import _sanitize_query  # reuse PII guardrails


@tool
def retrieve_resume_context(question: str) -> str:
    """Retrieve relevant resume context from the Pinecone index for the given question.

    This tool searches the existing Pinecone index identified by PINECONE_INDEX_NAME
    and returns the most relevant text chunks as plain text.
    """

    vector_store = get_existing_vector_store(PINECONE_INDEX_NAME)
    docs = search_relevant_data(question, vector_store)
    return "\n\n".join(doc.page_content for doc in docs)


SYSTEM_PROMPT = """You are an agent that answers questions about a resume.

You have access to a tool `retrieve_resume_context` that can look up
relevant parts of the indexed resume.

Rules:
1. Call tools when you need information from the resume.
2. Base your final answer only on information returned by tools.
3. If the resume context does not contain the answer, say you don't know
   or that the document does not contain that information.
4. Never invent facts, names, dates, or numbers.
5. Refuse requests that are illegal, harmful, hateful, or explicit.
6. Answer concisely and in the same language as the user's question.
"""


_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4.1-mini")
_agent = create_react_agent(_llm, [retrieve_resume_context])


def run_agentic_rag(query: str) -> str:
    """Run the agentic RAG flow for a single user query.

    - Applies PII sanitization to the query.
    - Lets the agent decide when to call the retrieval tool.
    - Returns the final answer message content as a string.
    """

    safe_query = _sanitize_query(query)
    result: Dict[str, Any] = _agent.invoke({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": safe_query},
        ]
    })

    messages = result.get("messages", [])
    if not messages:
        return "I could not generate a response."

    last = messages[-1]

    # LangChain messages (e.g. AIMessage) expose `.content`
    content = getattr(last, "content", "")

    # content may be a string or a list of parts depending on the model/tooling
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content:
        # join text parts if present
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "".join(parts).strip() or "I could not generate a response."

    return "I could not generate a response."
