import logging
import sys
from pathlib import Path

import streamlit as st
from components import (
    chat_form,
    inject_css,
    render_facts,
    render_header,
    render_messages,
    render_uploaded_list,
    set_page,
)
from utils.chatbot import get_response
from utils.climate_facts import get_random_fact

logging.getLogger("streamlit").setLevel(logging.WARNING)

# ensure project root is on sys.path so `from backend...` works
project_root = (
    Path(__file__).resolve().parents[1]
)  # -> c:\Users\bamos\finalYear\nlp_project
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# import backend functions
from backend.app.main import create_conversation, process_uploads, rag_ask
from backend.app.models.prompt import PromptCreate

DEFAULT_WELCOME = "Hello — I'm a government helper bot. Ask me about the climate, impacts, and solutions."

# Provide a short guard so users who run "python app.py" get a hint.
if __name__ == "__main__" and "streamlit" not in sys.modules:
    print("This app is a Streamlit app. Run it with:")
    print("  streamlit run app.py")
    sys.exit(0)


def start_new_conversation():
    """
    Call backend create_conversation and store a best-effort id in session_state['conversation_id'].
    Works with dict return or object with .id / .conversation_id attributes.
    """
    try:
        conv = create_conversation()
    except Exception:
        conv = None

    conv_id = None
    if isinstance(conv, dict):
        conv_id = conv.get("id") or conv.get("conversation_id")
    else:
        conv_id = getattr(conv, "id", None) or getattr(conv, "conversation_id", None)

    st.session_state["conversation_id"] = conv_id


# Page setup
set_page()
inject_css()

# Session state init
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "bot", "content": DEFAULT_WELCOME}]
    start_new_conversation()

if "current_fact" not in st.session_state:
    st.session_state["current_fact"] = get_random_fact()
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []


def handle_user_input(user_text, uploaded_file, file_url=None):
    if user_text:
        st.session_state["messages"].append({"role": "user", "content": user_text})
        resp = get_response(user_text)
        prompt = rag_ask(PromptCreate(query=user_text))
        resp = prompt.answer + f"\n\n*Confidence: {prompt.confidence:.2f}"

        logging.info(f"RAG answer: {resp}")
        logging.info(f"RAG source: {prompt.sources}")

        st.session_state["messages"].append({"role": "bot", "content": resp})

    # prefer local upload; if not provided and file_url is present, forward the URL string
    if uploaded_file:
        data = uploaded_file.read()
        if not data or len(data) == 0:
            st.error(f"Uploaded file {uploaded_file.name} appears to be empty.")
            try:
                uploaded_file.seek(0)
            except Exception:
                pass
            st.rerun()
        try:
            uploaded_file.seek(0)
        except Exception:
            pass

        try:
            meta = process_uploads([uploaded_file])
        except Exception as e:
            st.error(
                f"Failed to process upload: {getattr(e, 'args', ['Unknown error'])[0]}"
            )
            st.exception(e)
            st.rerun()

        st.session_state["uploaded_files"].append({
            "name": uploaded_file.name,
            "bytes": data,
            "type": uploaded_file.type,
            "metadata": meta,
        })
        st.success(f"Uploaded {uploaded_file.name}")

    elif file_url:
        # forward URL to backend loader (backend must accept http(s) URLs)
        try:
            meta = process_uploads([file_url])
        except Exception as e:
            st.error(
                f"Failed to process URL: {getattr(e, 'args', ['Unknown error'])[0]}"
            )
            st.exception(e)
            st.rerun()

        st.session_state["uploaded_files"].append({
            "name": file_url,
            "bytes": None,
            "type": "url",
            "metadata": meta,
        })
        st.success(f"Processed URL: {file_url}")

    st.rerun()


def on_new_fact():
    st.session_state["current_fact"] = get_random_fact()
    st.rerun()


# Layout
left_col, right_col = st.columns([3, 1])

with left_col:
    render_header()
    render_messages(st.session_state["messages"], DEFAULT_WELCOME)
    chat_form(handle_user_input)
    render_uploaded_list()
    if st.button("Reset conversation", use_container_width=True):
        st.session_state["messages"] = [{"role": "bot", "content": DEFAULT_WELCOME}]
        st.rerun()

with right_col:
    render_facts(st.session_state["current_fact"], on_new_fact)
