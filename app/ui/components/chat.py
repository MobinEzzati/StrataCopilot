# app/ui/components/chat.py
import streamlit as st


def render_evidence(evidence):
    if not evidence:
        return

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


def render_chat_history(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            if msg["role"] == "assistant":
                render_evidence(msg.get("evidence", []))


def add_user_message(state, content: str):
    state.messages.append(
        {
            "role": "user",
            "content": content,
        }
    )


def add_assistant_message(state, content: str, evidence=None):
    state.messages.append(
        {
            "role": "assistant",
            "content": content,
            "evidence": evidence or [],
        }
    )