import uuid
from langchain_core.documents import Document
from rag.chunking import chunk_documents
from vectorstore.chroma import get_vectorstore


def process_documents(docs: list[Document], doc_id: str) -> int:
    for doc in docs:
        doc.metadata["doc_id"] = doc_id

    chunks = chunk_documents(docs)

    for chunk in chunks:
        chunk.metadata["chunk_id"] = str(uuid.uuid4())

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    return len(chunks)
