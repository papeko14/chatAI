import streamlit as st
import requests
import json

# --- Configuration ---
N8N_WEBHOOK_URL = "https://rationally-tough-ant.ngrok-free.app/webhook/d8e551ba-6202-4544-be0a-74294ecff821" # Replace with your actual n8n webhook URL

# --- Streamlit UI ---
st.set_page_config(page_title="n8n Chatbot", layout="centered")
st.title("🤖 n8n Chatbot Demo")
st.write("Type your message and see n8n's response!")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        response.raise_for_status() # สำคัญ: ตรวจสอบ HTTP status code

        # *** จุดที่ต้องตรวจสอบ ***
        n8n_response_data = response.json()
        # แปลง JSON response เป็น Python dict/list

        # *** จุดที่ต้องตรวจสอบ ***
        # ตรงนี้คือส่วนที่ดึงข้อความจาก n8n_response_data
        n8n_message = n8n_response_data.get("reply", "No reply received from n8n.")

        # เพิ่มและแสดงผล
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
