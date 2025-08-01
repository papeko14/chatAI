import streamlit as st
import requests
import json
import os
# --- Configuration ---
N8N_WEBHOOK_URL = "https://rationally-tough-ant.ngrok-free.app/webhook/d8e551ba-6202-4544-be0a-74294ecff821" # Replace with your actual n8n webhook URL

# --- File-based Data Persistence ---
CHAT_HISTORY_FILE = "chat_history.json"
def load_chat_history():
    """Loads chat history from a JSON file."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
def save_chat_history(messages):
    """Saves chat history to a JSON file."""
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

# --- Streamlit UI ---
st.set_page_config(page_title="n8n Chatbot", layout="centered")
st.title("🤖 n8n Chatbot Demo")
st.write("Type your message and see n8n's response!")
# Load chat history from file on startup if it's not already in session_state


# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and n8n Integration ---
if prompt := st.chat_input("Say something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        payload = {"message": prompt}
        headers = {"Content-Type": "application/json"}
        response = requests.post(N8N_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        n8n_response_data = response.json()
        n8n_message = n8n_response_data.get("reply", "No reply received from n8n.")

        st.session_state.messages.append({"role": "assistant", "content": n8n_message})
        with st.chat_message("assistant"):
            st.markdown(n8n_message)

    except requests.exceptions.RequestException as e:
        error_message = f"Error connecting to n8n: {e}"
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
            st.markdown(error_message)
    except json.JSONDecodeError:
        error_message = "n8n returned an invalid JSON response."
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
            st.markdown(error_message)

    # --- Save the updated chat history to file ---
    save_chat_history(st.session_state.messages)
    st.rerun() # Rerun the app to update the display
