import streamlit as st
import json
import requests

def get_api_response(payload: dict, api_endpoint: str) -> dict:
    """
    Send a POST request to the API endpoint and return the JSON response.
    Raises an exception if the request fails.
    """
    response = requests.post(api_endpoint, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    # Set the page configuration with the roll number as the title
    roll_number = "Bajaj finserve project @ Ravi Kumar 22bcs10709" 
    st.set_page_config(page_title=roll_number, layout="wide")
    st.title(roll_number)
    
    st.markdown("### Enter your JSON input for the backend request")
    st.markdown("Example: `{ \"data\": [\"A\", \"C\", \"z\"] }`")
    
    # Retrieve API endpoint from secrets, or use default
    API_ENDPOINT = "https://finserv-mu.vercel.app/bfhl"
    
    # Initialize session state to store the API response
    if "result" not in st.session_state:
        st.session_state.result = None

    # Use a form to prevent re-running the entire script on every UI change
    with st.form("json_form", clear_on_submit=False):
        input_json = st.text_area("JSON Input", height=150, value='{"data": ["A", "C", "z"]}')
        submitted = st.form_submit_button("Submit")

    if submitted:
        # Validate JSON input
        try:
            payload = json.loads(input_json)
            if "data" not in payload:
                st.error("JSON must contain the key 'data'.")
            else:
                try:
                    result = get_api_response(payload, API_ENDPOINT)
                    st.session_state.result = result  # Persist the response
                    st.success("Successfully received response from backend!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend: {e}")
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please enter a valid JSON.")

    # If a response is available, display filtering options without resetting state
    if st.session_state.result is not None:
        st.markdown("### Filter the Response")
        selected_fields = st.multiselect(
            "Select fields to display:",
            options=["Alphabets", "Numbers", "Highest alphabet"]
        )
        
        # Prepare a filtered view of the response based on the dropdown selections
        display_data = {}
        if "Alphabets" in selected_fields:
            display_data["Alphabets"] = st.session_state.result.get("alphabets", [])
        if "Numbers" in selected_fields:
            display_data["Numbers"] = st.session_state.result.get("numbers", [])
        if "Highest alphabet" in selected_fields:
            display_data["Highest alphabet"] = st.session_state.result.get("highest_alphabet", [])
        
        if display_data:
            st.write("### Filtered Response")
            for key, value in display_data.items():
                st.write(f"**{key}:** {value}")
        else:
            st.info("No fields selected. Use the dropdown to view specific parts of the response.")
        
        with st.expander("View Full Response"):
            st.json(st.session_state.result)

if __name__ == "__main__":
    main()
