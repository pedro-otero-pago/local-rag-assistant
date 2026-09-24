# local-rag-assistant
Local RAG assistant that answers questions about your documents using Ollama and ChromaDB, with no external API calls.

## Project structure

- `document_processing.py` — extracts text from a PDF with pypdf and
  splits it into overlapping chunks with LangChain's
  RecursiveCharacterTextSplitter.
- `embeddings.py` — provides the local embedding model (Ollama's
  nomic-embed-text), used to convert text chunks into vectors.
- `store_vectors.py` — indexes chunks into a persistent ChromaDB store.
  Deduplicates by content hash, so re-running on the same document
  doesn't create duplicate entries, and new documents can be added
  later without reprocessing existing ones.