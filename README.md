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
- `rag_pipeline.py` — ties retrieval and generation together:
  retrieves the most relevant chunks for a question from the vector
  store, then prompts llama3.2 to answer using only that context,
  explicitly instructed to say when it doesn't know rather than
  answering from general knowledge.
- `app.py` — Streamlit chat interface: upload a PDF, process and index
  it, then ask questions in a conversational format (st.chat_message /
  st.chat_input) with full history kept in st.session_state, which
  persists across Streamlit's full-script re-runs on every interaction.


## Running the app

    streamlit run src/app.py

Upload a PDF, wait for it to be indexed, then ask questions about its
content in the text box that appears.