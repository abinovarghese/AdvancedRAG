MULTI_QUERY_PROMPT = """You are an AI assistant helping to generate multiple search queries.
Given the user question, generate 3 different versions of the question to retrieve relevant documents.
Provide these alternative questions separated by newlines.
Original question: {question}
Alternative questions:"""

HYDE_PROMPT = """Write a short passage that would answer the following question.
Do not say "I don't know". Write a plausible answer even if you're unsure.
Question: {question}
Passage:"""

RAG_PROMPT = """Use the following context to answer the question. If you cannot answer from the context, say so.
Always cite which source documents you used.

Context:
{context}

Question: {question}

Answer:"""
