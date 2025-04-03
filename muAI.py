import streamlit as st
import requests
from urllib.parse import quote

# Set up the page configuration
st.set_page_config(
    page_title="Ravi's AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to generate streaming response
def generate_response(user_input):
    encoded_input = quote(user_input)
    url = f'https://myai-882701280393.us-central1.run.app/stream/{encoded_input}'
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                yield chunk.decode('utf-8')
    except requests.exceptions.RequestException as e:
        yield f"⚠️ Error connecting to AI service: {str(e)}"

# Chat input and processing
if prompt := st.chat_input("Ask Ravi's AI anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create container for assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Stream the response
        for chunk in generate_response(prompt):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        
        # Finalize the response
        response_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar information
with st.sidebar:
    st.title("About")
    st.markdown("""
    ### Ravi's Personal AI Assistant
    Powered by:
    - Python flask
    - Streamlit for UI
    - hosted on Google Cloud Run
    - optimized for real-time text generation
    """)
    # github link ravibh5522
    st.markdown("[GitHub Profile](www.github.com/ravibh5522)")
    # linkedin link ravibh5522
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/ravibh5522/)")
    st.write("Version: 1.2")