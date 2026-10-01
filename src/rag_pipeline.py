from langchain_ollama import OllamaLLM
from store_vectors import create_vector_store

def answer_question(vector_store, question, k=3):
    relevant_chunks = vector_store.similarity_search(question, k=k)
    context = "\n\n".join(chunk.page_content for chunk in relevant_chunks)

    prompt = f"""Responde a la pregunta basándote únicamente en el siguiente contexto.
Si la respuesta no está en el contexto, di "No lo sé".

Contexto: {context}

Pregunta: {question}

Respuesta:"""

    llm = OllamaLLM(model="llama3.2")
    return llm.invoke(prompt)