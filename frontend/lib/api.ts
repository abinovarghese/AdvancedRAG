import type {
  Conversation,
  ConversationDetail,
  Document,
  Settings,
  ChatResponse,
} from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${url}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

// Chat
export async function sendMessage(
  message: string,
  conversationId?: string,
  useHyde = false
): Promise<ChatResponse> {
  return fetchJSON("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      use_hyde: useHyde,
    }),
  });
}

// Documents
export async function uploadDocuments(files: File[]): Promise<Document[]> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const res = await fetch(`${API}/api/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function ingestURL(url: string): Promise<Document> {
  return fetchJSON("/api/documents/url", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function listDocuments(): Promise<Document[]> {
  return fetchJSON("/api/documents");
}

export async function deleteDocument(id: string): Promise<void> {
  await fetchJSON(`/api/documents/${id}`, { method: "DELETE" });
}

// Conversations
export async function listConversations(): Promise<Conversation[]> {
  return fetchJSON("/api/conversations");
}

export async function createConversation(
  title = "New Chat"
): Promise<Conversation> {
  return fetchJSON("/api/conversations", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  return fetchJSON(`/api/conversations/${id}`);
}

export async function deleteConversation(id: string): Promise<void> {
  await fetchJSON(`/api/conversations/${id}`, { method: "DELETE" });
}

// Settings
export async function getSettings(): Promise<Settings> {
  return fetchJSON("/api/settings");
}

export async function updateSettings(
  data: Partial<Settings> & {
    openai_api_key?: string;
    watsonx_api_key?: string;
    watsonx_project_id?: string;
    watsonx_url?: string;
  }
): Promise<Settings> {
  return fetchJSON("/api/settings", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
