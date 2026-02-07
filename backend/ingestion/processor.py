import uuid
from langchain_core.documents import Document
from rag.chunking import chunk_documents
from vectorstore.chroma import get_vectorstore, reset_vectorstore_cache


def process_documents(docs: list[Document], doc_id: str) -> int:
    for doc in docs:
        doc.metadata["doc_id"] = doc_id

    chunks = chunk_documents(docs)

    for chunk in chunks:
        chunk.metadata["chunk_id"] = str(uuid.uuid4())

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    reset_vectorstore_cache()

    return len(chunks)
