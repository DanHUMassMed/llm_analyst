
from llm_analyst.core.exceptions import LLMAnalystsException
def get_embeddings_provider(provider_nm):
    embeddings = None
    match provider_nm:
        case "ollama":
            from langchain.embeddings import OllamaEmbeddings
            embeddings = OllamaEmbeddings(model="llama3")
        case "openai":
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
        case "huggingface":
            from langchain.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings()
        case _:
            raise LLMAnalystsException("Embedding provider not found.")

    return embeddings
