from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_hyde: bool = False


class Source(BaseModel):
    doc_name: str
    page: Optional[int] = None
    chunk_text: str
    relevance_score: float


class ChatResponse(BaseModel):
    message: str
    sources: list[Source]
    conversation_id: str


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: Optional[int]
    chunk_count: Optional[int]
    created_at: str


class URLIngestRequest(BaseModel):
    url: str


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationCreate(BaseModel):
    title: str = "New Chat"


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[list[Source]] = None
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: list[MessageOut]
    created_at: str
    updated_at: str


class SettingsOut(BaseModel):
    llm_provider: str
    openai_model: str
    watsonx_model: str
    chunk_size: int
    chunk_overlap: int
    retrieval_top_k: int
    rerank_top_k: int
    bm25_weight: float
    vector_weight: float


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: Optional[str] = None
    openai_model: Optional[str] = None
    watsonx_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    retrieval_top_k: Optional[int] = None
    rerank_top_k: Optional[int] = None
    bm25_weight: Optional[float] = None
    vector_weight: Optional[float] = None
