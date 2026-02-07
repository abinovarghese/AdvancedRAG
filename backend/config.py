from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    llm_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # WatsonX
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model: str = "ibm/granite-13b-chat-v2"
    watsonx_embedding_model: str = "ibm/slate-125m-english-rtrvr"

    # Storage
    chroma_persist_dir: str = "./chromadb"
    sqlite_db_path: str = "./data/advancedrag.db"

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 10
    rerank_top_k: int = 5
    bm25_weight: float = 0.4
    vector_weight: float = 0.6

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
