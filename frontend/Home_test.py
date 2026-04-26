import streamlit as st
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.ui.stats import init_state, add_user_message, add_assistant_message
from app.ui.services.api import ask_backend
from app.ui.components.sidebar import render_sidebar
from app.ui.components.Header import render_header, render_ingest_summary
from app.ui.components.chat import render_chat_history, render_evidence

# ✅ FIRST Streamlit command
st.set_page_config(
    page_title="StrataCopilot",
    page_icon="💬",
    layout="wide",
)


# THEN other imports


init_state()

backend_ok, k = render_sidebar()

render_header(st.session_state.selected_doc)
render_ingest_summary(st.session_state.last_ingest)
render_chat_history(st.session_state.messages)

prompt = st.chat_input("Ask a question about the uploaded document...")

if prompt:
    add_user_message(prompt)

    with st.chat_message("user"):
        st.write(prompt)

    if not backend_ok:
        assistant_text = "Backend is not running. Please start the FastAPI server on port 8001."
        add_assistant_message(assistant_text, [])
        with st.chat_message("assistant"):
            st.write(assistant_text)

    elif not st.session_state.documents:
        assistant_text = "Please upload and ingest a PDF first."
        add_assistant_message(assistant_text, [])
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
                    render_evidence(evidence)
                    add_assistant_message(answer, evidence)
                else:
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", "Failed to query backend.")
                    except Exception:
                        detail = "Failed to query backend."

                    st.write(detail)
                    add_assistant_message(detail, [])

        except Exception as e:
            error_text = f"Connection error while querying backend: {e}"
            with st.chat_message("assistant"):
                st.write(error_text)
            add_assistant_message(error_text, [])