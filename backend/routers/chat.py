import json
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.schemas import ChatRequest, ChatResponse
from rag.engine import rag_engine
from database import get_db, DB_PATH
import aiosqlite

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    async for db in get_db():
        # Create conversation if needed
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            await db.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conversation_id, request.message[:50], datetime.utcnow().isoformat(), datetime.utcnow().isoformat()),
            )

        # Save user message
        user_msg_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_msg_id, conversation_id, "user", request.message, datetime.utcnow().isoformat()),
        )

        # Run RAG
        answer, sources = rag_engine.query(request.message, use_hyde=request.use_hyde)

        # Save assistant message
        assistant_msg_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (assistant_msg_id, conversation_id, "assistant", answer, json.dumps([s.model_dump() for s in sources]), datetime.utcnow().isoformat()),
        )

        # Update conversation timestamp
        await db.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), conversation_id),
        )
        await db.commit()

        return ChatResponse(message=answer, sources=sources, conversation_id=conversation_id)


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("message", "")
            use_hyde = data.get("use_hyde", False)

            async with aiosqlite.connect(DB_PATH) as db:
                # Save user message
                user_msg_id = str(uuid.uuid4())
                await db.execute(
                    "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_msg_id, conversation_id, "user", question, datetime.utcnow().isoformat()),
                )
                await db.commit()

            # Stream response
            full_response = ""
            sources_data = []

            async for event in rag_engine.stream_query(question, use_hyde=use_hyde):
                if event["type"] == "token":
                    full_response += event["content"]
                    await websocket.send_json(event)
                elif event["type"] == "sources":
                    sources_data = event["sources"]
                    await websocket.send_json(event)

            # Send done signal
            await websocket.send_json({"type": "done"})

            # Save assistant message
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
