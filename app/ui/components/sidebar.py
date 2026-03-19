import streamlit as st
from app.ui.Services.api import check_backend, ingest_document
from app.ui.components.sidebar import render_sidebar


def render_sidebar(state):
    """
    Renders the sidebar UI and handles interactions.

    Args:
        state: st.session_state

    Returns:
        dict containing:
            - backend_ok (bool)
            - k (int)
    """

    with st.sidebar:
        st.title("StrataCopilot")
        st.caption("Enterprise document copilot")

        # -----------------------------
        # Backend status
        # -----------------------------
        backend_ok = check_backend()

        if backend_ok:
            st.success("Backend connected")
        else:
            st.error("Backend offline")

        st.markdown("---")

        # -----------------------------
        # Upload section
        # -----------------------------
        st.subheader("Add document")

        uploaded_file = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )

        if st.button("Ingest document", use_container_width=True):
            if not backend_ok:
                st.error("Backend is not running.")
            elif uploaded_file is None:
                st.warning("Please upload a PDF first.")
            else:
                try:
                    with st.spinner("Ingesting document..."):
                        response = ingest_document(uploaded_file)

                    if response.status_code == 200:
                        data = response.json()

                        state.last_ingest = data

                        doc_entry = {
                            "filename": data.get("filename"),
                            "num_chunks": data.get("num_chunks"),
                            "text_len": data.get("text_len"),
                            "preview": data.get("preview"),
                        }

                        # Avoid duplicates
                        existing_names = [doc["filename"] for doc in state.documents]
                        if doc_entry["filename"] not in existing_names:
                            state.documents.append(doc_entry)

                        state.selected_doc = doc_entry["filename"]

                        st.success("Document ingested successfully.")

                    else:
                        try:
                            error_data = response.json()
                            st.error(error_data.get("detail", "Failed to ingest document."))
                        except Exception:
                            st.error("Failed to ingest document.")

                except Exception as e:
                    st.error(f"Connection error: {e}")

        st.markdown("---")

        # -----------------------------
        # Documents list
        # -----------------------------
        st.subheader("Documents")

        if not state.documents:
            st.caption("No documents ingested yet.")
        else:
            for doc in state.documents:
                is_selected = state.selected_doc == doc["filename"]

                if st.button(
                    f"📄 {doc['filename']}",
                    use_container_width=True,
                    key=f"doc_{doc['filename']}"
                ):
                    state.selected_doc = doc["filename"]

                if is_selected:
                    st.caption(
                        f"Chunks: {doc['num_chunks']} • Text length: {doc['text_len']}"
                    )

        st.markdown("---")

        # -----------------------------
        # Query settings
        # -----------------------------
        st.subheader("Query settings")

        k = st.slider("Top-k chunks", 1, 10, 3)

        return {
            "backend_ok": backend_ok,
            "k": k
        }