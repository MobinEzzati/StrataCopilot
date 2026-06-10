import streamlit as st


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "documents" not in st.session_state:
        st.session_state.documents = []

    if "last_ingest" not in st.session_state:
        st.session_state.last_ingest = None

    if "selected_doc" not in st.session_state:
        st.session_state.selected_doc = None


def add_user_message(content: str):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": content,
        }
    )


def add_assistant_message(content: str, evidence=None):
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": content,
            "evidence": evidence or [],
        }
    )