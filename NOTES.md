## Document processing and chunking

load_pdf_text extracts text page by page with pypdf and concatenates it
into a single string. This has a real limitation worth noting: it
preserves no page boundaries or section separators — text from
consecutive pages is joined directly. This became visible with the
test PDF (slides from a PowerPoint export), where the same slide title
repeats at the start of many pages, so two identical titles sometimes
end up stuck together with no separator between them. This isn't
specific to this PDF — it's a general property of the extraction
approach, just more noticeable here because of the repeated titles.

split_text uses RecursiveCharacterTextSplitter (chunk_size=500,
chunk_overlap=50). It tries to split on paragraph breaks first, then
sentences, only falling back to splitting mid-sentence when a chunk
would otherwise be too large. The overlap means the last ~50 characters
of one chunk repeat at the start of the next, so a concept split across
a chunk boundary doesn't lose all its immediate context.

## Embeddings

Uses Ollama's nomic-embed-text model (via langchain-ollama) rather than
an external API, in line with the project's goal of running fully
locally. Each embedding is a 768-dimensional vector representing the
meaning of a chunk, not its literal words — this is what allows
retrieval to match a question like "how do you train a model as data
arrives gradually?" to a chunk about "aprendizaje incremental" even
without shared vocabulary.

## Vector store (ChromaDB)

First version used Chroma.from_texts() with a persist_directory,
without checking whether that directory already had content. Running
the script twice silently duplicated every chunk (48 instead of 24) —
from_texts() always appends, it never deduplicates. Since persistence
means the store is meant to survive across runs (e.g. the app
restarting), this needed a real fix, not just documenting it as a known
issue.

Fixed by giving each chunk a deterministic ID: an MD5 hash of its own
text content. Before adding anything, the existing IDs already in the
store are fetched, and only chunks whose hash isn't already present get
added. This solves duplication (re-running on the same PDF adds 0 new
chunks) and, as a side effect, makes it possible to later add a second
document to the same store without reprocessing or duplicating the
first one's chunks.