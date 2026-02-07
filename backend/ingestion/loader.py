from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    TextLoader,
    JSONLoader,
)

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".xls": UnstructuredExcelLoader,
    ".md": UnstructuredMarkdownLoader,
    ".csv": CSVLoader,
    ".txt": TextLoader,
    ".json": JSONLoader,
}


def load_file(file_path: str) -> list[Document]:
    ext = Path(file_path).suffix.lower()
    loader_cls = LOADER_MAP.get(ext)
    if loader_cls is None:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == ".json":
        loader = loader_cls(file_path, jq_schema=".", text_content=False)
    else:
        loader = loader_cls(file_path)

    docs = loader.load()
    for doc in docs:
        doc.metadata["source_file"] = Path(file_path).name
    return docs


def load_url(url: str) -> list[Document]:
    loader = WebBaseLoader(url)
    docs = loader.load()
    for doc in docs:
        doc.metadata["source_file"] = url
    return docs
