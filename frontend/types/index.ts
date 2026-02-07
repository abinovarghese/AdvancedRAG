export interface Source {
  doc_name: string;
  page: number | null;
  chunk_text: string;
  relevance_score: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[] | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number | null;
  chunk_count: number | null;
  created_at: string;
}

export interface Settings {
  llm_provider: string;
  openai_model: string;
  watsonx_model: string;
  chunk_size: number;
  chunk_overlap: number;
  retrieval_top_k: number;
  rerank_top_k: number;
  bm25_weight: number;
  vector_weight: number;
}

export interface ChatResponse {
  message: string;
  sources: Source[];
  conversation_id: string;
}

export interface StreamEvent {
  type: "token" | "sources" | "done";
  content?: string;
  sources?: Source[];
}
