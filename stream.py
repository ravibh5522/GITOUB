import streamlit as st
import requests
import json
import time # For simulating typing effect

# --- Configuration ---
# Make sure your Flask API is running, typically on http://localhost:5000
FLASK_API_URL = "https://askbhimup-882701280393.europe-west1.run.app/chat"

# --- Streamlit App Setup ---
st.set_page_config(page_title="Dr. Ambedkar RAG Chatbot", page_icon="📚")
st.title("📚 Dr. Ambedkar's Writings Chatbot")
st.markdown("Ask me anything about Dr. B.R. Ambedkar's writings!")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "summaries" in message and message["summaries"]:
            st.expander("Context Summaries").markdown("\n".join([f"- {s}" for s in message["summaries"]]))

# --- Chat Input and API Interaction ---
if prompt := st.chat_input("Your query..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        retrieved_summaries = []

        try:
            # Prepare the payload for the Flask API
            # Only send the last N messages as history to avoid exceeding token limits
            # For simplicity, sending all for now, but in production, limit history.
            chat_history_for_api = []
            for msg in st.session_state.messages:
                # Exclude the very last user message that is currently being processed
                if msg["role"] == "user" and msg["content"] == prompt:
                    continue
                chat_history_for_api.append({"role": msg["role"], "parts": msg["content"]})


            payload = {
                "query": prompt,
                "history": chat_history_for_api,
                "top_k": 5 # You can make this configurable
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream" # Important for SSE
            }

            # Make the POST request to your Flask API with streaming enabled
            # stream=True ensures the response is not downloaded all at once
            with requests.post(FLASK_API_URL, json=payload, headers=headers, stream=True) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data:"):
                                try:
                                    json_data = json.loads(decoded_line[len("data:"):])
                                    if "text" in json_data:
                                        full_response += json_data["text"]
                                        message_placeholder.markdown(full_response + "▌") # Add a blinking cursor effect
                                    elif "summaries" in json_data:
                                        retrieved_summaries = json_data["summaries"]
                                    elif "error" in json_data:
                                        full_response += f"\n\nError from API: {json_data['error']}"
                                        message_placeholder.markdown(full_response)
                                        break # Stop processing on error
                                except json.JSONDecodeError:
                                    st.error(f"Error decoding JSON from API: {decoded_line}")
                                    break
                    
                    # Update placeholder with final response (remove cursor)
                    message_placeholder.markdown(full_response)

                    # Display summaries if available
                    if retrieved_summaries:
                        with st.expander("Context Summaries"):
                            st.markdown("\n".join([f"- {s}" for s in retrieved_summaries]))

                    # Add assistant's full response and summaries to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "summaries": retrieved_summaries
                    })

                else:
                    error_message = f"API Error: Status {response.status_code}"
                    try:
                        error_details = response.json()
                        error_message += f" - {error_details.get('error', 'Unknown error')}"
                    except json.JSONDecodeError:
                        error_message += f" - Could not parse error response: {response.text}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the Flask API. Please ensure it is running at "
                     f"`{FLASK_API_URL}` and accessible.")
            st.session_state.messages.append({"role": "assistant", "content": "Connection error."})
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"An unexpected error occurred: {e}"})

# --- Clear Chat Button ---
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()

st.sidebar.info("This chatbot uses a Retrieval-Augmented Generation (RAG) model to answer questions based on Dr. B.R. Ambedkar's writings. The responses are streamed from a Flask API.")

