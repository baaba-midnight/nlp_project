import sys
import streamlit as st
from utils.chatbot import get_response
from utils.climate_facts import get_random_fact

# Provide a short guard so users who run "python app.py" get a hint.
if __name__ == "__main__" and "streamlit" not in sys.modules:
    print("This app is a Streamlit app. Run it with:")
    print("  streamlit run app.py")
    sys.exit(0)

DEFAULT_WELCOME = "Hello — I'm a government helper bot. Ask me about the climate, impacts, and solutions."

st.set_page_config(page_title="Climate Chat", layout="wide")

# Custom CSS for a modern, polished look
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .chat-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        text-align: right;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-message-bot {
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        text-align: left;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    .chat-message-bot-welcome {
        background: white;
        color: #000;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        text-align: left;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    .fact-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
        font-size: 16px;
        line-height: 1.6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #667eea;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:hover {
        border-color: #764ba2;
        box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);
    }
    .stTextInput>div>div>input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 12px rgba(102, 126, 234, 0.6);
    }
    .stTextInput>div>div>input::placeholder {
        color: white !important;
    }
    .stTextInput label {
        color: #000 !important;
        font-weight: 600;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #000 !important;
        font-weight: 700;
    }
    .climate-facts-header {
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "bot", "content": DEFAULT_WELCOME}]
if "current_fact" not in st.session_state:
    st.session_state["current_fact"] = get_random_fact()

# Layout: main two columns (chat + facts)
left_col, right_col = st.columns([3, 1])

with left_col:
    st.markdown("<h1 style='color: #000;'>🌍 Ghana Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Show messages
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-message-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            if msg["content"] == DEFAULT_WELCOME:
                st.markdown(f"<div class='chat-message-bot-welcome'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message-bot'>{msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #ddd; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Input and controls
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message", placeholder="Ask about climate change, impacts, or solutions...")
        submitted = st.form_submit_button("Send")
        if submitted and user_input and user_input.strip():
            st.session_state["messages"].append({"role": "user", "content": user_input.strip()})
            response = get_response(user_input.strip())
            st.session_state["messages"].append({"role": "bot", "content": response})
            st.experimental_rerun()  # refresh to show the new messages

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset conversation", use_container_width=True):
            st.session_state["messages"] = [{"role": "bot", "content": DEFAULT_WELCOME}]
            st.experimental_rerun()

with right_col:
    st.markdown("<div style='text-align: start;'><h3 class='climate-facts-header'>💡 Climate Facts</h3></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='fact-card'>{st.session_state['current_fact']}</div>", unsafe_allow_html=True)

    if st.button("Get New Fact", use_container_width=True):
        st.session_state["current_fact"] = get_random_fact()
        st.experimental_rerun()

