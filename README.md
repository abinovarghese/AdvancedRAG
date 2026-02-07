# Advanced RAG Pipeline

A Retrieval-Augmented Generation pipeline that demonstrates the difference between naive RAG and an advanced multi-stage retrieval approach using LangChain.

## Why Advanced RAG?

Naive RAG retrieves documents based on simple vector similarity, which often misses relevant context or returns redundant results. This project implements a **multi-stage retrieval pipeline** that significantly improves answer quality:

```
Query --> [BM25 + Vector Search] --> Ensemble Retriever --> Redundancy Filter --> Long Context Reorder --> BGE Reranker --> LLM
```

### Pipeline Stages

1. **Hybrid Retrieval** -- Combines BM25 (keyword-based) and vector similarity search via an Ensemble Retriever with weighted scoring
2. **Redundancy Filtering** -- Removes near-duplicate documents using embedding similarity
3. **Long Context Reordering** -- Reorders documents to place the most relevant ones at the beginning and end (mitigating the "lost in the middle" problem)
4. **BGE Reranking** -- Uses a cross-encoder model (`BAAI/bge-reranker-large`) to score and select the top documents by relevance
5. **Answer Generation** -- Passes the refined context to OpenAI for final answer synthesis

## Tech Stack

- **LangChain** -- Orchestration framework for chaining retrieval and generation
- **ChromaDB** -- Vector store for document embeddings
- **OpenAI** -- Embeddings (`text-embedding-ada-002`) and LLM for generation
- **Sentence Transformers** -- Cross-encoder reranking with BGE
- **BM25** -- Sparse keyword retrieval via `rank_bm25`

## Project Structure

```
advanced_RAG.py     # Advanced pipeline: ensemble retrieval + compression + reranking
native_RAG.py       # Baseline naive RAG for comparison
bgereranker.py      # Custom BGE cross-encoder reranker component
store_docs.py       # Document chunking and ChromaDB persistence
web_doc_loader.py   # Web page loader for ingesting documents
get_db.py           # ChromaDB connection helper
main.py             # Entry point: runs both pipelines and compares results
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

```bash
git clone https://github.com/abinovarghese/AdvancedRAG.git
cd AdvancedRAG
pip install -r requirements.txt
```

### Usage

```bash
export OPENAI_API_KEY="your-api-key"
python main.py
```

The script loads a web document, stores it in ChromaDB, then runs both the naive and advanced RAG pipelines so you can compare the quality of responses.

## Key Takeaway

The advanced pipeline produces more accurate, contextually relevant answers by combining multiple retrieval strategies and filtering techniques -- demonstrating that **how you retrieve matters as much as what you retrieve**.
