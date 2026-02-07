import os
import uuid
import tempfile
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import DocumentOut, URLIngestRequest
from ingestion.loader import load_file, load_url
from ingestion.processor import process_documents
from vectorstore.chroma import delete_document_vectors
from database import get_db

router = APIRouter()


@router.post("/documents/upload", response_model=list[DocumentOut])
async def upload_documents(files: list[UploadFile] = File(...)):
    results = []
    async for db in get_db():
        for file in files:
            doc_id = str(uuid.uuid4())
            suffix = os.path.splitext(file.filename or "")[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            try:
                docs = load_file(tmp_path)
                chunk_count = process_documents(docs, doc_id)
            finally:
                os.unlink(tmp_path)

            now = datetime.utcnow().isoformat()
            await db.execute(
                "INSERT INTO documents (id, filename, file_type, file_size, chunk_count, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, file.filename, suffix, len(content), chunk_count, now),
            )
            results.append(DocumentOut(
                id=doc_id,
                filename=file.filename or "",
                file_type=suffix,
                file_size=len(content),
                chunk_count=chunk_count,
                created_at=now,
            ))
        await db.commit()
    return results


@router.post("/documents/url", response_model=DocumentOut)
async def ingest_url(request: URLIngestRequest):
    doc_id = str(uuid.uuid4())
    docs = load_url(request.url)
    chunk_count = process_documents(docs, doc_id)
    now = datetime.utcnow().isoformat()

    async for db in get_db():
        await db.execute(
            "INSERT INTO documents (id, filename, file_type, file_size, chunk_count, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, request.url, "url", 0, chunk_count, now),
        )
        await db.commit()

    return DocumentOut(
        id=doc_id, filename=request.url, file_type="url",
        file_size=0, chunk_count=chunk_count, created_at=now,
    )


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents():
    async for db in get_db():
        cursor = await db.execute("SELECT * FROM documents ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [
            DocumentOut(
                id=row["id"], filename=row["filename"], file_type=row["file_type"],
                file_size=row["file_size"], chunk_count=row["chunk_count"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    async for db in get_db():
        cursor = await db.execute("SELECT id FROM documents WHERE id = ?", (doc_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Document not found")

        delete_document_vectors(doc_id)
        await db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        await db.commit()

    return {"status": "deleted"}
