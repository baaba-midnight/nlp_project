import streamlit as st


def set_page():
    st.set_page_config(page_title="Climate Chat", layout="wide")


def inject_css():
    st.markdown(
        """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .chat-message-user { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 16px; border-radius: 18px; margin: 8px 0; text-align: right; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .chat-message-bot { background: white; color: #333; padding: 12px 16px; border-radius: 18px; margin: 8px 0; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.08); border-left: 4px solid #667eea; }
    .chat-message-bot-welcome { background: white; color: #000; padding: 12px 16px; border-radius: 18px; margin: 8px 0; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.08); border-left: 4px solid #667eea; }
    .fact-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; margin: 16px 0; box-shadow: 0 6px 12px rgba(102,126,234,0.3); font-size:16px; line-height:1.6; }
    .stButton>button { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; border:none; border-radius:8px; padding:10px 20px; font-weight:600; }
    .stTextInput>div>div>input { border-radius:8px; border:2px solid #667eea; transition: all .3s ease; }
    .stTextInput>div>div>input::placeholder { color:#9aa4b2 !important; font-style:italic !important; opacity:0.95 !important; }
    .stTextInput label { color:#000 !important; font-weight:600; }
</style>
""",
        unsafe_allow_html=True,
    )


def render_header(title="🌍 Ghana Chatbot"):
    st.markdown(f"<h1 style='color: #000;'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='border:1px solid #ddd; margin:20px 0;'>", unsafe_allow_html=True
    )


def render_messages(messages, default_welcome):
    for msg in messages:
        if msg.get("role") == "user":
            st.markdown(
                f"<div class='chat-message-user'>{msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            if msg.get("content") == default_welcome:
                st.markdown(
                    f"<div class='chat-message-bot-welcome'>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-message-bot'>{msg['content']}</div>",
                    unsafe_allow_html=True,
                )


def chat_form(on_submit_fn):
    """
    Simple chat form with text input, file uploader, and a URL field.
    Calls on_submit_fn(user_text, uploaded_file, file_url).
    """
    with st.form(key="chat_form", clear_on_submit=False):
        user_input = st.text_input("Your question", key="user_input")
        uploaded_file = st.file_uploader(
            "Upload file (PDF, txt, etc.)", type=None, key="file_uploader"
        )
        file_url = st.text_input("Or paste a file URL (http/https)", key="file_url")
        submitted = st.form_submit_button("Send")
        if submitted:
            on_submit_fn(
                user_input.strip() if user_input else "",
                uploaded_file,
                file_url.strip() if file_url else None,
            )


def render_uploaded_list():
    if "uploaded_files" in st.session_state and st.session_state["uploaded_files"]:
        st.markdown("**Uploaded files:**")
        for f in st.session_state["uploaded_files"]:
            st.markdown(f"- {f['name']}")


def render_facts(current_fact, on_new_fact):
    st.markdown(f"<div class='fact-card'>{current_fact}</div>", unsafe_allow_html=True)
    if st.button("Get New Fact", use_container_width=True):
        on_new_fact()
