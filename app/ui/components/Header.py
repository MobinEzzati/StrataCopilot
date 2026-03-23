import streamlit as st


def render_header(selected_doc):
    st.title("💬 StrataCopilot")
    st.caption("Ask grounded questions over your uploaded documents using retrieval + LLM reasoning.")

    if selected_doc:
        st.info(f"Active document: {selected_doc}")
    else:
        st.info("Upload and ingest a document from the sidebar to start chatting.")


def render_ingest_summary(last_ingest):
    if not last_ingest:
        return

    with st.expander("Latest ingestion details"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Filename", last_ingest.get("filename", "N/A"))
        c2.metric("Chunks", last_ingest.get("num_chunks", 0))
        c3.metric("Text length", last_ingest.get("text_len", 0))
        st.write("Preview:")
        st.write(last_ingest.get("preview", ""))