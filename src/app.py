import streamlit as st
from document_processing import load_pdf_text, split_text
from store_vectors import create_vector_store
from rag_pipeline import answer_question

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Asistente RAG local")

uploaded_file = st.file_uploader("Sube un PDF", type="pdf")

if uploaded_file is not None:
    temp_path = f"data/{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    with st.spinner("Procesando documento..."):
        text = load_pdf_text(temp_path)
        chunks = split_text(text)
        st.session_state.vector_store = create_vector_store(chunks)

    st.success(f"Documento procesado: {len(st.session_state.vector_store.get()['ids'])} fragmentos indexados")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Haz una pregunta sobre el documento")

if question and st.session_state.vector_store is not None:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            answer = answer_question(st.session_state.vector_store, question)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})