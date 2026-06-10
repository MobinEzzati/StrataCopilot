
import requests
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")



st.set_page_config(
    page_title="StrataCopilot",
    page_icon="💬",
    layout="wide",
)

# -----------------------------
# Helpers
# -----------------------------
def check_backend() -> bool:
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def ingest_document(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }
    return requests.post(f"{API_URL}/ingest", files=files, timeout=120)


def ask_backend(question: str, k: int):
    payload = {"question": question, "k": k}
    return requests.post(f"{API_URL}/ask", json=payload, timeout=120)


# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "last_ingest" not in st.session_state:
    st.session_state.last_ingest = None

if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("StrataCopilot")
    st.caption("Enterprise document copilot")

    backend_ok = check_backend()
    if backend_ok:
        st.success("Backend connected")
    else:
        st.error("Backend offline")

    st.markdown("---")
    st.subheader("Add document")

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed")

    if st.button("Ingest document", use_container_width=True):
        if not backend_ok:
            st.error("Backend is not running on port 8001.")
        elif uploaded_file is None:
            st.warning("Please upload a PDF first.")
        else:
            try:
                with st.spinner("Ingesting document..."):
                    response = ingest_document(uploaded_file)

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.last_ingest = data

                    doc_entry = {
                        "filename": data.get("filename"),
                        "num_chunks": data.get("num_chunks"),
                        "text_len": data.get("text_len"),
                        "preview": data.get("preview"),
                    }

                    existing_names = [doc["filename"] for doc in st.session_state.documents]
                    if doc_entry["filename"] not in existing_names:
                        st.session_state.documents.append(doc_entry)

                    st.session_state.selected_doc = doc_entry["filename"]
                    st.success("Document ingested successfully.")
                else:
                    try:
                        error_data = response.json()
                        st.error(error_data.get("detail", "Failed to ingest document."))
                    except Exception:
                        st.error("Failed to ingest document.")
            except requests.RequestException as e:
                st.error(f"Connection error: {e}")

    st.markdown("---")
    st.subheader("Documents")

    if not st.session_state.documents:
        st.caption("No documents ingested yet.")
    else:
        for doc in st.session_state.documents:
            is_selected = st.session_state.selected_doc == doc["filename"]
            button_label = f"📄 {doc['filename']}"
            if st.button(button_label, use_container_width=True, key=f"doc_{doc['filename']}"):
                st.session_state.selected_doc = doc["filename"]

            if is_selected:
                st.caption(f"Chunks: {doc['num_chunks']} • Text length: {doc['text_len']}")

    st.markdown("---")
    st.subheader("Query settings")
    k = st.slider("Top-k chunks", 1, 10, 3)


# -----------------------------
# Main Header
# -----------------------------
st.title("💬 StrataCopilot")
st.caption("Ask grounded questions over your uploaded documents using retrieval + LLM reasoning.")

if st.session_state.selected_doc:
    st.info(f"Active document: {st.session_state.selected_doc}")
else:
    st.info("Upload and ingest a document from the sidebar to start chatting.")

# -----------------------------
# Show last ingest summary
# -----------------------------
if st.session_state.last_ingest:
    with st.expander("Latest ingestion details"):
        data = st.session_state.last_ingest
        c1, c2, c3 = st.columns(3)
        c1.metric("Filename", data.get("filename", "N/A"))
        c2.metric("Chunks", data.get("num_chunks", 0))
        c3.metric("Text length", data.get("text_len", 0))
        st.write("Preview:")
        st.write(data.get("preview", ""))

# -----------------------------
# Chat History
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        if msg["role"] == "assistant" and msg.get("evidence"):
            with st.expander("View evidence"):
                for item in msg["evidence"]:
                    st.markdown(
                        f"**Rank {item.get('rank')}** • "
                        f"Chunk {item.get('chunk_index')} • "
                        f"Score {item.get('score', 0):.3f}"
                    )
                    st.write(f"**Source:** {item.get('source_file', 'N/A')}")
                    st.write(item.get("text", ""))
                    st.markdown("---")

# -----------------------------
# Chat Input
# -----------------------------
prompt = st.chat_input("Ask a question about the uploaded document...")

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    if not backend_ok:
        assistant_text = "Backend is not running. Please start the FastAPI server on port 8001."
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_text,
                "evidence": [],
            }
        )
        with st.chat_message("assistant"):
            st.write(assistant_text)

    elif not st.session_state.documents:
        assistant_text = "Please upload and ingest a PDF first."
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_text,
                "evidence": [],
            }
        )
        with st.chat_message("assistant"):
            st.write(assistant_text)

    else:
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = ask_backend(prompt, k)

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    evidence = data.get("evidence", [])

                    st.write(answer)

                    if evidence:
                        with st.expander("View evidence"):
                            for item in evidence:
                                st.markdown(
                                    f"**Rank {item.get('rank')}** • "
                                    f"Chunk {item.get('chunk_index')} • "
                                    f"Score {item.get('score', 0):.3f}"
                                )
                                st.write(f"**Source:** {item.get('source_file', 'N/A')}")
                                st.write(item.get("text", ""))
                                st.markdown("---")

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "evidence": evidence,
                        }
                    )

                else:
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", "Failed to query backend.")
                    except Exception:
                        detail = "Failed to query backend."

                    st.write(detail)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": detail,
                            "evidence": [],
                        }
                    )

        except requests.RequestException as e:
            error_text = f"Connection error while querying backend: {e}"
            with st.chat_message("assistant"):
                st.write(error_text)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_text,
                    "evidence": [],
                }
            )