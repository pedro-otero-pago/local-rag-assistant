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

## RAG pipeline (retrieval + generation)

answer_question ties the whole pipeline together: embeds the question,
retrieves the k=3 most similar chunks from ChromaDB via
similarity_search, joins their text into a single context block, and
sends both the context and the question to llama3.2 with an explicit
instruction to answer only from that context and say "I don't know"
otherwise — this is the core mechanism that keeps the system grounded
in the actual documents instead of the model's general training
knowledge.

The prompt instructions are written in Spanish, not English, even
though the rest of the codebase is in English. This is intentional: the
test PDF and any questions asked about it are in Spanish, so keeping
the prompt in the same language avoids making the model switch
languages mid-instruction, which smaller local models like llama3.2:3b
handle less reliably than larger hosted models. I considered making the
prompt language configurable (a dict of templates keyed by language
code), but decided against it for now — the parameter would only
control the instruction language, not translate or force the response
language, so it wouldn't actually solve the real use case (asking in a
different language than the document) and would add complexity without
a genuine benefit at this stage.

Tested with two questions: one answerable from the document ("¿Qué es
el concept drift?", correctly answered using the relevant chunk) and
one unrelated to it ("¿Cuál es la capital de Francia?", correctly
answered "No lo sé" instead of answering from general knowledge) —
confirming the grounding instruction works as intended, not just in
theory.