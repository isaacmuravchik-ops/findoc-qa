import streamlit as st
from ingest import extract_text, chunk_text, build_index
from rag import answer_question

st.set_page_config(page_title="FinDoc Q&A (by Isaac Muravchik)", page_icon="📄")
st.title("📄 FinDoc Q&A (by Isaac Muravchik)")
st.caption("Upload a financial document and ask questions — answers come with page citations.")

uploaded = st.file_uploader("Upload a PDF (e.g., a 10-K)", type="pdf")

if uploaded:
    # Re-index only when a new file is uploaded, not on every keystroke.
    if "collection" not in st.session_state or st.session_state.get("name") != uploaded.name:
        with st.spinner("Indexing document…"):
            with open("temp.pdf", "wb") as f:
                f.write(uploaded.getbuffer())
            pages = extract_text("temp.pdf")
            chunks = chunk_text(pages)
            st.session_state.collection = build_index(chunks)
            st.session_state.name = uploaded.name
        st.success(f"Indexed {len(chunks)} chunks from {uploaded.name}")

    question = st.text_input("Ask a question about the document:")
    if question:
        with st.spinner("Thinking…"):
            answer, pages = answer_question(st.session_state.collection, question)
        st.markdown("### Answer")
        st.write(answer.replace("$", "\\$"))
        st.caption(f"Sources: pages {', '.join(map(str, pages))}")