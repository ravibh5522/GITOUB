import streamlit as st
import requests
import json

# API URL
api_url = "https://llmchat-882701280393.us-central1.run.app/chat"

st.title("💬 LLM Chatbot")

# Initialize chat history if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to call the chat API
def call_chat_api(user_input, history):
    payload = {
        "query": user_input,
        "history": history,
        "top_k": 3
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json().get("text", "Error: No response from model.")
    except Exception as e:
        return f"Error calling API: {e}"

# User input
user_input = st.text_input("You:", key="user_input")

if st.button("Send") and user_input:
    # Add user input to history
    st.session_state.chat_history.append({"role": "user", "parts": [user_input]})

    # Get model response
    model_response = call_chat_api(user_input, st.session_state.chat_history)

    # Add model response to history
    st.session_state.chat_history.append({"role": "model", "parts": [model_response]})

# Display chat history
for message in st.session_state.chat_history:
    role = "👤 You" if message["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{role}:** {message['parts'][0]}")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.chat_history = []