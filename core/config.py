import os 
from dotenv import load_dotenv


load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Pinecone configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


# Ensure that the required keys are set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is not set in the environment variables.")
