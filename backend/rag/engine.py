from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from providers.factory import get_llm, get_streaming_llm
from vectorstore.chroma import get_vectorstore
from rag.prompts import RAG_PROMPT
from models.schemas import Source
from config import settings


class RAGEngine:
    def _fast_retrieve(self, question: str):
        """Simple vector similarity search — fast."""
        vectorstore = get_vectorstore()
        return vectorstore.similarity_search_with_relevance_scores(
            question, k=settings.rerank_top_k
        )

    def query(self, question: str, use_hyde: bool = False) -> tuple[str, list[Source]]:
        llm = get_llm()

        results = self._fast_retrieve(question)

        if not results:
            return "I don't have enough context to answer this question. Please upload relevant documents first.", []

        docs = [doc for doc, score in results]
        scores = [score for doc, score in results]

        # Attach scores to metadata
        for doc, score in zip(docs, scores):
            doc.metadata["relevance_score"] = score

        context = "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source_file', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})

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
        streaming_llm = get_streaming_llm()

        results = self._fast_retrieve(question)

        if not results:
            yield {"type": "token", "content": "I don't have enough context to answer this question. Please upload relevant documents first."}
            yield {"type": "sources", "sources": []}
            return

        docs = [doc for doc, score in results]
        scores = [score for doc, score in results]

        for doc, score in zip(docs, scores):
            doc.metadata["relevance_score"] = score

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
