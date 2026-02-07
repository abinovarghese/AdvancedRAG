import chromadb
from langchain_community.vectorstores import Chroma
from providers.factory import get_embeddings
from config import settings


def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name="advancedrag",
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def delete_document_vectors(doc_id: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection("advancedrag")
    results = collection.get(where={"doc_id": doc_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])
