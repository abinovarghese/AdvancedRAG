MULTI_QUERY_PROMPT = """You are an AI assistant helping to generate multiple search queries.
Given the user question, generate 3 different versions of the question to retrieve relevant documents.
Provide these alternative questions separated by newlines.
Original question: {question}
Alternative questions:"""

HYDE_PROMPT = """Write a short passage that would answer the following question.
Do not say "I don't know". Write a plausible answer even if you're unsure.
Question: {question}
Passage:"""

RAG_PROMPT = """You are a knowledgeable assistant. Use the following context to provide a detailed, comprehensive answer to the question.

Instructions:
- Give thorough, well-structured answers with explanations and examples from the context
- Use bullet points or numbered lists when appropriate for clarity
- Include relevant details, definitions, and relationships between concepts
- If the context covers multiple aspects of the question, address all of them
- Cite the source documents you used
- If the context is insufficient, say what you can answer and what is missing

Context:
{context}

Question: {question}

Detailed Answer:"""
