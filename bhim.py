import streamlit as st
import requests
import json
from streamlit_chat import message
import time

# Set page config
st.set_page_config(
    page_title="Bodhi AI - Ambedkar Scholar",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = "https://askbhimup-559132211786.europe-west1.run.app/chat"
HEADERS = {'Content-Type': 'application/json'}

# Custom CSS for styling
st.markdown("""
<style>
    /* Main chat container */
    .stChatFloatingInputContainer {
        border-radius: 15px;
        padding: 15px;
        background-color: #f9f9f9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a365d;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #2a4b8d;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #1a365d;
        color: white;
    }
    
    /* Custom chat messages */
    .user-message {
        background-color: #2a4b8d !important;
        color: white !important;
        border-radius: 15px 15px 0 15px !important;
        padding: 12px;
        margin-bottom: 10px;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background-color: #e6f0ff !important;
        color: #333 !important;
        border-radius: 15px 15px 15px 0 !important;
        padding: 12px;
        margin-bottom: 10px;
        max-width: 80%;
        margin-right: auto;
    }
    
    /* Avatar styling */
    .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .user-avatar {
        background-color: #1a365d;
        color: white;
    }
    
    .bot-avatar {
        background-color: #2a4b8d;
        color: white;
    }
    
    /* Hide Streamlit footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    # Initialize core state variables
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = []
    
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    
    if 'active_conversation' not in st.session_state:
        st.session_state.active_conversation = "default"
    
    # Initialize settings with unique keys
    if 'streaming_setting' not in st.session_state:
        st.session_state.streaming_setting = True
    
    if 'show_refs_setting' not in st.session_state:
        st.session_state.show_refs_setting = False

init_session_state()

# Sidebar
with st.sidebar:
    st.title("📚 Bodhi AI")
    st.subheader("Dr. Ambedkar Scholar")
    st.markdown("---")
    
    # New chat button
    if st.button("➕ New Chat", key="new_chat"):
        if st.session_state.current_conversation:
            conversation_id = f"conv_{int(time.time())}"
            st.session_state.conversations[conversation_id] = st.session_state.current_conversation.copy()
            st.session_state.active_conversation = conversation_id
        st.session_state.current_conversation = []
        st.session_state.history = []
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.current_conversation = []
        st.session_state.history = []
    
    # Conversations history
    st.markdown("---")
    st.subheader("Conversations")
    
    # Add current conversation to history if not empty
    if st.session_state.current_conversation and "default" not in st.session_state.conversations:
        st.session_state.conversations["default"] = st.session_state.current_conversation.copy()
    
    # Display conversation history
    for conv_id, conv in list(st.session_state.conversations.items()):
        if st.button(f"💬 {conv_id if conv_id != 'default' else 'Current Conversation'}", key=f"conv_{conv_id}"):
            st.session_state.current_conversation = conv.copy()
            st.session_state.active_conversation = conv_id
            st.session_state.history = []

    # Settings
    st.markdown("---")
    st.subheader("Settings")
    
    # Use unique keys for settings widgets
    st.session_state.streaming_setting = st.checkbox(
        "Enable Streaming", 
        value=st.session_state.streaming_setting, 
        key="streaming_cb"
    )
    
    st.session_state.show_refs_setting = st.checkbox(
        "Show References", 
        value=st.session_state.show_refs_setting, 
        key="show_refs_cb"
    )

# Main content
st.title("Bodhi AI")
st.caption("An AI assistant specializing in Dr. B.R. Ambedkar's work and philosophy")

# Chat container
chat_container = st.container()

# Display chat messages with custom styling
with chat_container:
    for msg in st.session_state.current_conversation:
        if msg["role"] == "user":
            # User message with custom styling
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
                    <div>
                        <div class="user-message">{msg["content"]}</div>
                    </div>
                    <div class="avatar user-avatar">U</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Bot message with custom styling
            st.markdown(
                f"""
                <div style="display: flex; margin-bottom: 15px;">
                    <div class="avatar bot-avatar">BA</div>
                    <div>
                        <div class="bot-message">{msg["content"]}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# References section
if st.session_state.show_refs_setting and st.session_state.current_conversation:
    last_response = next((msg for msg in reversed(st.session_state.current_conversation) 
                         if msg["role"] == "assistant"), None)
    
    if last_response and "references" in last_response and last_response["references"]:
        with st.expander("🔍 References from Ambedkar's Work", expanded=False):
            for ref in last_response["references"]:
                st.markdown(f"""
                <div style="background-color: #f0f7ff; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <p style="margin: 0; font-size: 14px;"><strong>Page {ref.get('page_index', 'N/A')}</strong></p>
                    <p style="margin: 0; font-size: 13px;">{ref.get('summary', '')}</p>
                    <p style="margin: 0; font-size: 12px; color: #666;">Relevance: {ref.get('retrieval_score', '0%')}</p>
                </div>
                """, unsafe_allow_html=True)

# Chat input
def send_message():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return
    
    # Add user message to history
    user_msg = {
        "id": f"msg_{len(st.session_state.current_conversation)}",
        "role": "user",
        "content": user_input
    }
    st.session_state.current_conversation.append(user_msg)
    st.session_state.history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    
    # Clear input
    st.session_state.user_input = ""
    
    # Create placeholder for bot response
    bot_msg_id = f"msg_{len(st.session_state.current_conversation)}"
    bot_msg = {
        "id": bot_msg_id,
        "role": "assistant",
        "content": ""
    }
    st.session_state.current_conversation.append(bot_msg)
    
    # Prepare API request
    payload = {
        "query": user_input,
        "history": st.session_state.history,
        "stream": st.session_state.streaming_setting
    }
    
    # Make API request
    if st.session_state.streaming_setting:
        # Streaming response
        response = requests.post(
            API_URL, 
            json=payload, 
            headers=HEADERS, 
            stream=True
        )
        
        content = []
        references = None
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        data = json.loads(decoded_line)
                        if "chunk" in data:
                            content.append(data["chunk"])
                            # Update bot message incrementally
                            st.session_state.current_conversation[-1]["content"] = ''.join(content)
                            # Rerun to update UI
                            st.rerun()
                        elif "references" in data:
                            references = data["references"]
                    except json.JSONDecodeError:
                        continue
        else:
            content = ["Error: Could not connect to the API"]
        
        # Final update
        st.session_state.current_conversation[-1]["content"] = ''.join(content)
        if references:
            st.session_state.current_conversation[-1]["references"] = references
        
        # Add to history
        st.session_state.history.append({
            "role": "model",
            "parts": [{"text": ''.join(content)}]
        })
    else:
        # Non-streaming response
        response = requests.post(
            API_URL, 
            json=payload, 
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.current_conversation[-1]["content"] = data.get("answer_text", "")
            if "references" in data:
                st.session_state.current_conversation[-1]["references"] = data["references"]
            
            # Add to history
            st.session_state.history.append({
                "role": "model",
                "parts": [{"text": data.get("answer_text", "")}]
            })
        else:
            st.session_state.current_conversation[-1]["content"] = "Error: Could not connect to the API"

# Chat input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Ask about Dr. Ambedkar's work:",
        key="user_input",
        placeholder="Type your question here...",
        height=80,
        max_chars=1000
    )
    
    submit_button = st.form_submit_button(
        label="Send",
        on_click=send_message,
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("Bodhi AI - Specializing in Dr. B.R. Ambedkar's Philosophy and Writings")