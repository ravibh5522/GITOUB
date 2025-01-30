import streamlit as st
import requests
import json
import logging

# --- Set up logging ---
logging.basicConfig(level=logging.DEBUG)

# API Base URL
API_BASE_URL = "https://llmchatwithimg-1073743898611.us-central1.run.app"
IMAGE_DB_URL = "https://storage.googleapis.com/llmimages/"

# --- Session State Management ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = 1
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {}

# --- Function to send message to API ---
def send_message_to_api(query, history):
    api_endpoint = f"{API_BASE_URL}/chat"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "query": query,
        "history": history
    }
    print("\n--- Sending API Request ---") # Debugging print
    print("Payload History sent to API:", payload.get("history")) # Debugging print

    try:
        with requests.post(api_endpoint, headers=headers, json=payload, stream=True, timeout=30) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line)
                        print("\n--- Received SSE Event ---") # Debugging print
                        print("Event:", event) # Debugging print
                        yield event
                    except json.JSONDecodeError as e:
                        logging.error(f"JSONDecodeError: Could not decode SSE line: {line}. Error: {e}")
                        print(f"Could not decode SSE line: {line}. Error: {e}")
                        yield {"type": "error", "content": "Error processing server response."}
                        break
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        logging.error(f"API request exception: {e}")
        yield {"type": "error", "content": f"API request failed: {e}"}
        yield None

# --- Function to start a new chat ---
def start_new_chat():
    st.session_state.current_chat_id += 1
    st.session_state.messages = []
    st.session_state.chat_titles[st.session_state.current_chat_id] = "New Chat"
    st.session_state.chat_history[st.session_state.current_chat_id] = []
    print("\n--- New Chat Started ---") # Debugging print
    print("st.session_state.chat_history:", st.session_state.chat_history) # Debugging print


# --- Function to load a chat ---
def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_history.get(chat_id, [])
    print(f"\n--- Chat Loaded: Chat ID {chat_id} ---") # Debugging print
    print("st.session_state.chat_history:", st.session_state.chat_history) # Debugging print


# --- Streamlit UI ---
st.title("LLM Chat with Images")

# --- Sidebar ---
with st.sidebar:
    st.subheader("Chat History")
    if st.button("New Chat", on_click=start_new_chat):
        pass

    chat_ids = sorted(st.session_state.chat_history.keys(), reverse=True)
    if not st.session_state.chat_titles:
        st.session_state.chat_titles[1] = "Chat 1"

    for chat_id in chat_ids:
        title = st.session_state.chat_titles.get(chat_id, f"Chat {chat_id}")
        if st.button(f"Chat {chat_id}: {title[:20]}...", key=f"chat_{chat_id}_button", on_click=lambda cid=chat_id: load_chat(cid)):
            pass

    st.markdown("---")
    st.markdown("*(Select a chat from history or start a new one)*")

# --- Main Chat Area ---
if st.session_state.current_chat_id in st.session_state.chat_history:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "images" in message and message["images"]:
                if message["images"]:
                    st.write("Relevant Images:")
                    cols = st.columns(min(len(message["images"]), 3))
                    for i, img_url in enumerate(message["images"]):
                        if i < 3:
                            with cols[i]:
                                st.image(img_url, use_column_width=True)
            if message["role"] == "assistant" and "summaries" in message and message["summaries"]:
                if message["summaries"]:
                    with st.expander("Document Summaries"):
                        for summary in message["summaries"]:
                            st.write(summary)


# Chat input
if prompt := st.chat_input("Ask me anything"):
    current_chat_id = st.session_state.current_chat_id
    if current_chat_id not in st.session_state.chat_history:
        st.session_state.chat_history[current_chat_id] = []
        st.session_state.chat_titles[current_chat_id] = prompt[:20] + "..."

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_history[current_chat_id].append({"role": "user", "content": prompt})
    print("\n--- User Input ---") # Debugging print
    print("User prompt:", prompt) # Debugging print
    print("st.session_state.chat_history (after user input):", st.session_state.chat_history) # Debugging print


    with st.chat_message("user"):
        st.markdown(prompt)

    api_history = [{"role": msg["role"], "parts": [msg["content"]]}
                   for msg in st.session_state.chat_history[current_chat_id] if msg["role"] != "user"]

    print("\n--- Prepared API History ---") # Debugging print
    print("api_history sent to API:", api_history) # Debugging print


    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        image_urls = []
        summaries = []

        with st.spinner("Thinking..."):
            for event in send_message_to_api(prompt, api_history):
                if event:
                    if event.get("type") == "error":
                        full_response = event.get("content", "An error occurred.")
                        message_placeholder.markdown(full_response)
                        image_urls = []
                        summaries = []
                        break

                    if event.get("type") == "chunk":
                        chunk_text = event.get("content", "")
                        full_response += chunk_text
                        message_placeholder.markdown(full_response + "▌")

                    elif event.get("type") == "final":
                        full_response = event.get("content", full_response)
                        image_paths = event.get("images", [])
                        summaries = event.get("summaries", [])
                        api_response_history = event.get("history", [])

                        print("\n--- Final API Response Event ---") # Debugging print
                        print("API Response Event (final):", event) # Debugging print
                        print("API Response History (event.get('history')):", api_response_history) # Debugging print


                        for img_id in image_paths:
                            img_url = f"{IMAGE_DB_URL}{img_id}"
                            image_urls.append(img_url)

                        if api_response_history:
                            st.session_state.chat_history[current_chat_id] = [
                                {"role": msg["role"], "content": msg["parts"][0] if isinstance(msg["parts"], list) and msg["parts"] else ""}
                                for msg in api_response_history
                            ]
                            print("\n--- st.session_state.chat_history UPDATED ---") # Debugging print
                            print("Updated st.session_state.chat_history:", st.session_state.chat_history) # Debugging print


            else:
                if not full_response:
                    full_response = "No response from API."
                    image_urls = []
                    summaries = []

        message_placeholder.markdown(full_response)

        if image_urls:
            st.write("Relevant Images:")
            cols = st.columns(min(len(image_urls), 3))
            for i, img_url in enumerate(image_urls):
                if i < 3:
                    with cols[i]:
                        st.image(img_url, use_column_width=True)
        if summaries:
            with st.expander("Document Summaries"):
                for summary in summaries:
                    st.write(summary)


        assistant_message = {"role": "assistant", "content": full_response, "images": image_urls if image_urls else [], "summaries": summaries if summaries else []}
        st.session_state.messages.append(assistant_message)


# No need for extra st.chat_message("assistant") here anymore