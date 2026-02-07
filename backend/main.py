import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import aiosqlite
from database import init_db, DB_PATH
from rag.engine import rag_engine
from routers import chat, documents, conversations, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Advanced RAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("message", "")
            use_hyde = data.get("use_hyde", False)

            async with aiosqlite.connect(DB_PATH) as db:
                user_msg_id = str(uuid.uuid4())
                await db.execute(
                    "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_msg_id, conversation_id, "user", question, datetime.utcnow().isoformat()),
                )
                await db.commit()

            full_response = ""
            sources_data = []

            async for event in rag_engine.stream_query(question, use_hyde=use_hyde):
                if event["type"] == "token":
                    full_response += event["content"]
                    await websocket.send_json(event)
                elif event["type"] == "sources":
                    sources_data = event["sources"]
                    await websocket.send_json(event)

            await websocket.send_json({"type": "done"})

            async with aiosqlite.connect(DB_PATH) as db:
                assistant_msg_id = str(uuid.uuid4())
                await db.execute(
                    "INSERT INTO messages (id, conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (assistant_msg_id, conversation_id, "assistant", full_response, json.dumps(sources_data), datetime.utcnow().isoformat()),
                )
                await db.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (datetime.utcnow().isoformat(), conversation_id),
                )
                await db.commit()

    except WebSocketDisconnect:
        pass
