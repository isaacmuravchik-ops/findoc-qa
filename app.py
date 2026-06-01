import streamlit as st
from ingest import extract_text, chunk_text, build_index
from rag import answer_question

st.set_page_config(page_title="FinDoc Q&A", page_icon="📄")
st.title("📄 FinDoc Q&A")
st.caption("Upload a financial document and ask questions — answers come with page citations.")

uploaded = st.file_uploader("Upload a PDF (e.g., a 10-K)", type="pdf")

if uploaded:
    # Reject oversized files before doing any work.
    if uploaded.size > 20 * 1024 * 1024:   # 20 MB
        st.error("That PDF is over 20 MB. Please upload a smaller file.")
        st.stop()

    # Re-index only when a new file is uploaded, not on every keystroke.
    if "collection" not in st.session_state or st.session_state.get("name") != uploaded.name:
        with st.spinner("Indexing document…"):
            with open("temp.pdf", "wb") as f:
                f.write(uploaded.getbuffer())
            pages = extract_text("temp.pdf")
            chunks = chunk_text(pages)
            if not chunks:
                st.error("Couldn't extract any text from this PDF — "
                         "it may be a scanned image rather than a text document.")
                st.stop()
            st.session_state.collection = build_index(chunks)
            st.session_state.name = uploaded.name
        st.success(f"Indexed {len(chunks)} chunks from {uploaded.name}")

    question = st.text_input("Ask a question about the document:")
    if question:
        with st.spinner("Thinking…"):
            try:
                answer, pages = answer_question(st.session_state.collection, question)
            except Exception:
                answer, pages = None, None
                st.error("Something went wrong generating the answer — please try again in a moment.")
        if answer is not None:
            st.markdown("### Answer")
            st.write(answer.replace("$", "\\$"))
            if pages:
                st.caption(f"Sources: pages {', '.join(map(str, pages))}")