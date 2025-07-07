
import streamlit as st
import requests
import json
import os

# --- Configuration ---
# IMPORTANT: Replace this with the actual URL of your deployed orchestrator Cloud Function.
# You can also set this as an environment variable in your Streamlit deployment environment.
ORCHESTRATOR_CF_URL = os.environ.get(
    "ORCHESTRATOR_CF_URL",
    "https://us-central1-wf-hack25dfw-647.cloudfunctions.net/orchestrator_v2"
)

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Well-Sec Howdy!", page_icon="🤖")

st.title("🤖 Well-Sec Howdy!")
st.markdown(
    """
    Ask me questions about company policies (data privacy, employee conduct,
    software usage, travel expenses, security incidents).
    """
)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User role selection (for testing sensitive data filtering)
user_role = st.sidebar.radio(
    "Select User Role:",
    ("normal", "super"),
    index=0, # Default to normal user
    help="Choose 'normal' to test sensitive data filtering, or 'super' for full access."
)
st.sidebar.info(f"Current User Role: **{user_role.capitalize()}**")

# --- Function to call the Orchestrator Cloud Function ---
def call_orchestrator(query, role):
    payload = {
        "query": query,
        "user_role": role
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        # Streamlit apps run in a secure environment, so direct HTTP calls are fine.
        response = requests.post(ORCHESTRATOR_CF_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the chatbot backend: {e}")
        return {"response": f"Sorry, I'm having trouble connecting to the service. Please try again later. (Error: {e})"}
    except json.JSONDecodeError:
        st.error("Received an invalid response from the chatbot backend.")
        return {"response": "Sorry, I received an unreadable response from the service."}

# Chat input
if prompt := st.chat_input("What's your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show thinking message
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Call the orchestrator Cloud Function
            response_data = call_orchestrator(prompt, user_role)
            bot_response = response_data.get("response", "An unexpected error occurred.")
            st.markdown(bot_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Optional: Clear chat history button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit and Google Cloud Functions.")
