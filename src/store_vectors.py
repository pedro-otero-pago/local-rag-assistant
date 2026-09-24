import hashlib
from langchain_chroma import Chroma
from embeddings import get_embedding_model

def create_vector_store(chunks, persist_directory="chroma_db"):
    embedding_model = get_embedding_model()

    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
    )

    chunk_ids = [hashlib.md5(chunk.encode()).hexdigest() for chunk in chunks]
    existing_ids = set(vector_store.get()["ids"])

    new_chunks = [c for c, cid in zip(chunks, chunk_ids) if cid not in existing_ids]
    new_ids = [cid for cid in chunk_ids if cid not in existing_ids]

    if new_chunks:
        vector_store.add_texts(texts=new_chunks, ids=new_ids)

    return vector_store