from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from providers.factory import get_llm, get_streaming_llm
from rag.retrieval import multi_query_retrieve, hyde_retrieve, get_hybrid_retriever
from rag.reranking import rerank_documents
from rag.postprocessing import remove_redundant, reorder_long_context
from rag.prompts import RAG_PROMPT
from models.schemas import Source


class RAGEngine:
    def query(self, question: str, use_hyde: bool = False) -> tuple[str, list[Source]]:
        llm = get_llm()

        # Retrieval
        docs = multi_query_retrieve(question, llm)

        if use_hyde:
            hyde_docs = hyde_retrieve(question, llm)
            seen = {d.page_content[:200] for d in docs}
            for d in hyde_docs:
                if d.page_content[:200] not in seen:
                    docs.append(d)
                    seen.add(d.page_content[:200])

        # Postprocessing
        docs = remove_redundant(docs)
        docs = reorder_long_context(docs)

        # Reranking
        docs = rerank_documents(question, docs)

        if not docs:
            return "I don't have enough context to answer this question. Please upload relevant documents first.", []

        # Build context
        context = "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source_file', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

        # Generate
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

        # Build sources
        sources = [
            Source(
                doc_name=doc.metadata.get("source_file", "unknown"),
                page=doc.metadata.get("page"),
                chunk_text=doc.page_content[:300],
                relevance_score=round(doc.metadata.get("relevance_score", 0.0), 4),
            )
            for doc in docs
        ]

        return answer, sources

    async def stream_query(self, question: str, use_hyde: bool = False):
        llm = get_llm()
        streaming_llm = get_streaming_llm()

        # Retrieval
        docs = multi_query_retrieve(question, llm)

        if use_hyde:
            hyde_docs = hyde_retrieve(question, llm)
            seen = {d.page_content[:200] for d in docs}
            for d in hyde_docs:
                if d.page_content[:200] not in seen:
                    docs.append(d)
                    seen.add(d.page_content[:200])

        docs = remove_redundant(docs)
        docs = reorder_long_context(docs)
        docs = rerank_documents(question, docs)

        if not docs:
            yield {"type": "token", "content": "I don't have enough context to answer this question."}
            yield {"type": "sources", "sources": []}
            return

        context = "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source_file', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        chain = prompt | streaming_llm

        async for chunk in chain.astream({"context": context, "question": question}):
            token = chunk.content if hasattr(chunk, "content") else str(chunk)
            if token:
                yield {"type": "token", "content": token}

        sources = [
            Source(
                doc_name=doc.metadata.get("source_file", "unknown"),
                page=doc.metadata.get("page"),
                chunk_text=doc.page_content[:300],
                relevance_score=round(doc.metadata.get("relevance_score", 0.0), 4),
            )
            for doc in docs
        ]
        yield {"type": "sources", "sources": [s.model_dump() for s in sources]}


rag_engine = RAGEngine()
