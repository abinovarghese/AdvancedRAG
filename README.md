# RAG Forge

A production-grade, full-stack Retrieval-Augmented Generation application with a Next.js frontend, FastAPI backend, multi-provider LLM support, and advanced retrieval techniques.

![Next.js](https://img.shields.io/badge/Next.js_14-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=flat-square)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Next.js 14 Frontend                     │
│   Chat  ·  Document Management  ·  Settings  ·  History  │
└──────────────────────┬──────────────────────────────┘
                       │ REST + WebSocket (streaming)
┌──────────────────────┴──────────────────────────────┐
│                FastAPI Backend                        │
│   RAG Engine  ·  Multi-Provider LLM  ·  Doc Ingestion   │
│   ChromaDB Vectors  ·  SQLite  ·  Conversation Manager  │
└─────────────────────────────────────────────────────┘
```

## Features

**RAG Pipeline**
- Vector similarity search with ChromaDB
- Multi-format document ingestion (PDF, DOCX, PPTX, XLSX, MD, CSV, TXT, JSON, URL)
- Semantic chunking with configurable chunk size and overlap
- Source citation with relevance scores on every response

**Multi-Provider LLM Support**
- **Groq** (free) -- Llama 3.1 with sub-second inference
- **OpenAI** -- GPT-4o-mini / GPT-4o
- **Google Gemini** -- Gemini 2.0 Flash
- **IBM WatsonX** -- Granite models
- Runtime provider switching without restart

**Frontend**
- Streaming responses via WebSocket with typing indicator
- Drag-and-drop document upload with progress
- Expandable source citation cards below AI messages
- Conversation sidebar with create, switch, delete
- Settings modal for provider config and RAG parameter tuning
- Dark/light theme with system preference detection
- Responsive layout -- sidebar collapses on mobile

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 -- upload a document and start asking questions.

### Docker

```bash
docker-compose up
```

## Project Structure

```
backend/
├── main.py                  # FastAPI app + WebSocket endpoint
├── config.py                # Pydantic settings
├── database.py              # SQLite (conversations, messages, documents)
├── providers/               # LLM abstraction (OpenAI, Groq, Gemini, WatsonX)
├── rag/                     # RAG engine, chunking, retrieval, prompts
├── ingestion/               # Multi-format document loader + processor
├── vectorstore/             # ChromaDB operations
├── routers/                 # API routes (chat, documents, conversations, settings)
└── models/                  # Pydantic schemas

frontend/
├── app/                     # Next.js 14 App Router
├── components/              # Chat, Sidebar, Documents, Settings, UI
├── lib/                     # API client, WebSocket hook
└── types/                   # TypeScript interfaces
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat` | Send message, get RAG response |
| WS | `/ws/chat/{id}` | Streaming chat via WebSocket |
| POST | `/api/documents/upload` | Upload document(s) |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/{id}` | Delete document + vectors |
| POST | `/api/documents/url` | Ingest from URL |
| GET | `/api/conversations` | List conversations |
| POST | `/api/conversations` | Create new conversation |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| GET | `/api/settings` | Get current config |
| PUT | `/api/settings` | Update provider/RAG settings |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11, LangChain, Pydantic |
| LLM Providers | Groq, OpenAI, Google Gemini, IBM WatsonX |
| Vector Store | ChromaDB with HuggingFace embeddings |
| Database | SQLite (aiosqlite) |
| Deployment | Docker, docker-compose |
