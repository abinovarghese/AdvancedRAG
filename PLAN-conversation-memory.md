# Plan: Conversation Memory in RAG Pipeline

## Problem
RAG Forge stores conversation history in the database (messages table) but **never feeds it back** into the retrieval or generation steps. Every query is treated as a standalone question. This means:

- Follow-up questions fail ("Tell me more about that", "What about section 3?")
- Pronoun references are lost ("What does *it* do?" after discussing a specific tool)
- The chat UI gives users the illusion of a conversation, but the backend is stateless per-query

## Goal
Make the RAG pipeline conversation-aware so that prior messages are included in context for both **query reformulation** (better retrieval) and **answer generation** (coherent multi-turn dialogue).

## Design

### Query Reformulation (Contextual Compression)
Before retrieval, use the LLM to rewrite the user's latest message into a standalone question that incorporates conversation context. This is critical because retrieval operates on the query alone — "Tell me more about that" retrieves nothing useful.

Example:
```
History:  User: "What is LangChain?"  Assistant: "LangChain is a framework for..."
New msg:  "How does it handle memory?"
Rewritten: "How does LangChain handle memory?"
```

### Answer Generation
Pass a sliding window of recent messages alongside the retrieved context so the LLM generates coherent, conversation-aware answers.

### Token Budget
Use a sliding window of the **last 10 messages** (5 turns), truncated to ~2000 tokens. This keeps costs predictable while covering most follow-up scenarios.

## Changes

### 1. Add conversation history prompt to `backend/rag/prompts.py`

Add two new prompt templates:

```python
CONDENSE_QUESTION_PROMPT = """Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that captures the full context.

Chat History:
{chat_history}

Follow-up Question: {question}

Standalone Question:"""
```

Update `RAG_PROMPT` to include an optional `chat_history` block:

```python
RAG_PROMPT = """You are a knowledgeable assistant. Use the following context to answer the question.
...
{chat_history_block}
Context:
{context}

Question: {question}
...
"""
```

The `{chat_history_block}` will be empty string when there's no history (preserving current behavior) or a formatted block like:
```
Conversation so far:
User: What is LangChain?
Assistant: LangChain is a framework for...
```

### 2. Add history loading utility to `backend/rag/engine.py`

Add a method `_load_chat_history(conversation_id: str) -> list[dict]` that:
- Queries the messages table for the given conversation_id
- Returns the last 10 messages as `[{"role": "user", "content": "..."}, ...]`
- Returns empty list if no conversation_id or no history

### 3. Add query condensation to `backend/rag/engine.py`

Add a method `_condense_question(question: str, chat_history: list[dict]) -> str` that:
- If chat_history is empty, returns the question unchanged
- Otherwise, formats history and calls LLM with `CONDENSE_QUESTION_PROMPT`
- Returns the standalone question for retrieval

### 4. Update `RAGEngine._retrieve()` signature

Change from:
```python
def _retrieve(self, question: str) -> list[Document]
```
To:
```python
def _retrieve(self, question: str, conversation_id: str | None = None) -> list[Document]
```

Inside `_retrieve`:
1. Load chat history if conversation_id is provided
2. Condense the question using history
3. Use the condensed question for all retrieval strategies (hybrid, multi-query, HyDE, simple)

### 5. Update `RAGEngine.query()` and `stream_query()`

Both methods already receive `use_hyde` but not `conversation_id`. Update signatures:

```python
def query(self, question: str, conversation_id: str | None = None) -> tuple[str, list[Source]]
async def stream_query(self, question: str, conversation_id: str | None = None)
```

In both methods:
1. Call `_retrieve(question, conversation_id)` instead of `_retrieve(question)`
2. Load chat history (reuse from retrieve step or load once and pass through)
3. Format `chat_history_block` for the RAG prompt
4. Pass it into the prompt template

### 6. Update `backend/routers/chat.py`

Pass `conversation_id` to the engine:
```python
# Before
answer, sources = rag_engine.query(request.message, use_hyde=request.use_hyde)

# After
answer, sources = rag_engine.query(request.message, conversation_id=conversation_id)
```

### 7. Update `backend/main.py` (WebSocket chat handler)

Pass `conversation_id` to stream_query:
```python
# Before
async for event in rag_engine.stream_query(question, use_hyde=use_hyde):

# After
async for event in rag_engine.stream_query(question, conversation_id=conversation_id):
```

### 8. Remove `use_hyde` from API surface

The `use_hyde` parameter on `ChatRequest` and the WebSocket message is now redundant — HyDE is controlled globally via settings. Remove it from:
- `ChatRequest` schema (schemas.py)
- `chat.py` router
- `main.py` WebSocket handler
- `query()` / `stream_query()` signatures
- Frontend `useHyde` parameter in `api.ts` and `websocket.ts`

## Files to Modify
1. `backend/rag/prompts.py` — add CONDENSE_QUESTION_PROMPT, update RAG_PROMPT
2. `backend/rag/engine.py` — add history loading, query condensation, pass conversation_id through pipeline
3. `backend/routers/chat.py` — pass conversation_id to engine
4. `backend/main.py` — pass conversation_id to stream_query
5. `backend/models/schemas.py` — remove use_hyde from ChatRequest
6. `frontend/lib/api.ts` — remove useHyde param from sendMessage
7. `frontend/lib/websocket.ts` — remove useHyde param

## No Frontend UI Changes Needed
The frontend already sends `conversation_id` through the WebSocket URL path and via `ChatRequest`. The conversation memory is fully backend-side and transparent to the user.

## Verification
1. Start a conversation: "What is RAG?" — get a normal answer
2. Follow up: "What are its main components?" — should correctly understand "its" = RAG
3. Follow up: "Tell me more about the retrieval step" — should know we're discussing RAG retrieval
4. Start a new conversation — should have no memory bleed from the previous one
5. Test with no conversation_id (stateless mode) — should work exactly as before
6. Check backend logs for condensed question output to verify reformulation is happening
