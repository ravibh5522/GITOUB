import streamlit as st
import requests
import json

# --- Configuration ---
# URL of your Flask backend API
API_URL = "https://askbhimup-559132211786.europe-west1.run.app/chat"  # Update with your actual API URL

# --- Helper Function to Call API ---
def call_chat_api(query: str, history: list):
    """
    Calls the backend Flask API to get a response.

    Args:
        query (str): The user's input query.
        history (list): The conversation history in the API's expected format.

    Returns:
        dict: The JSON response from the API, or an error dictionary.
    """
    payload = {
        "query": query,
        "history": history
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: Could not connect to the Bodhi AI server. Please ensure the backend is running. Details: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Failed to decode the server's response. The server may have returned an invalid format.")
        return None

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Bodhi AI",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Bodhi AI")
st.caption("An AI assistant specializing in the writings and philosophy of Dr. B.R. Ambedkar.")

# --- Session State Initialization ---
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
# Loop through the existing messages and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message is from the assistant and has references, display them
        if message["role"] == "assistant" and "references" in message and message["references"]:
            with st.expander("View Sources"):
                for ref in message["references"]:
                    st.metric(label="Retrieval Score", value=ref.get('retrieval_score', 'N/A'))
                    st.info(
                        f"""
                        **Page Index:** {ref.get('page_index', 'N/A')}
                        \n**Summary:** {ref.get('summary', 'No summary provided.')}
                        """
                    )

# --- Handle User Input ---
if prompt := st.chat_input("Ask a question about Dr. Ambedkar's work..."):
    # 1. Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare data and call the API
    with st.chat_message("assistant"):
        with st.spinner("Bodhi AI is thinking..."):
            # Prepare history in the format the API expects
            api_history = []
            for msg in st.session_state.messages[:-1]: # Exclude the current user prompt
                if msg["role"] == "user":
                    api_history.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    api_history.append({"role": "model", "parts": [msg["content"]]})
            
            # Call the backend
            response_data = call_chat_api(prompt, api_history)

        # 3. Process and display the response
        if response_data and "error" not in response_data:
            answer = response_data.get("answer_text", "Sorry, I couldn't formulate a response.")
            references = response_data.get("references", [])

            # Display the main answer
            st.markdown(answer)

            # Display the references in a collapsible expander
            if references:
                with st.expander("View Sources"):
                    for ref in references:
                        # Use st.metric for a nice visual of the score
                        st.metric(label="Retrieval Score", value=ref.get('retrieval_score', 'N/A'))
                        # Use st.info or st.container to group reference details
                        st.info(
                            f"""
                            **Page Index:** {ref.get('page_index', 'N/A')}
                            \n**Summary:** {ref.get('summary', 'No summary provided.')}
                            """
                        )
            
            # Add the complete assistant response (with references) to the session state
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "references": references
            })

        elif response_data and "error" in response_data:
            # Handle errors returned from the API
            st.error(f"API Error: {response_data['error']}")
            # Add an error message to the chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Sorry, an error occurred: {response_data['error']}",
                "references": []
            })
        else:
            # Handle connection errors or other issues where response_data is None
            # The error is already displayed by st.error in the API call function
            # We add a placeholder to the chat history
             st.session_state.messages.append({
                "role": "assistant", 
                "content": "I was unable to process your request. Please try again later.",
                "references": []
            })