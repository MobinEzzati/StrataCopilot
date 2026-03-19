import requests
import streamlit as st

API_URL = "http://127.0.0.1:8001"

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