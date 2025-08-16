import streamlit as st
import requests
import json
import os
import pandas as pd
import csv

# --- Configuration ---
# URL ของ n8n webhook
N8N_WEBHOOK_URL = "https://rationally-tough-ant.ngrok-free.app/webhook-test/d8e551ba-6202-4544-be0a-74294ecff821"

def load_chat_history(machine_name):
    """
    ฟังก์ชันสำหรับโหลดประวัติการแชทจากไฟล์ JSON ตามชื่อเครื่องจักร
    """
    chat_history_file = f"{machine_name}.json"
    if os.path.exists(chat_history_file):
        try:
            with open(chat_history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_chat_history(machine_name, messages):
    """
    ฟังก์ชันสำหรับบันทึกประวัติการแชทลงในไฟล์ JSON ตามชื่อเครื่องจักร
    """
    chat_history_file = f"{machine_name}.json"
    with open(chat_history_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

# --- Streamlit UI ---
st.set_page_config(page_title="n8n Chatbot", layout="centered")

# --- Sidebar for machine selection ---
with st.sidebar:
    st.title("Main Menu")
    
    # Dropdown menu สำหรับเลือกเครื่องจักร
    zone = ('Exsample','iso10816-3')
    machine_options = ('FAN 2', 'FAN 1', 'PUMP 1', 'PUMP 2', 'PUMP 3',
                       'BENCH TMPLT VRSPD', 'BENCH DA3'
                       , 'EGL-ISO10816-3'
                       ,'FLC-ISO10816-3'
                       , 'MV-x ISO10816-3'
                       , '1A-1 - Pump' 
                       , 'Gear EX'
                       ,'Pump Gateway')
    selected_zone = st.selectbox(
        "Select zone of machine:",
        zone,
        key="zone" # ใช้ key เพื่อให้ Streamlit จัดการ session state
    )
    selected_machine = st.selectbox(
        "Select a machine:",
        machine_options,
        key="selected_machine" # ใช้ key เพื่อให้ Streamlit จัดการ session state
    )
    st.markdown("---")
st.title(f"🤖 Chat with {selected_machine}")
st.write("Type your message and see n8n's response!")

# --- Main App Logic ---

# ตรวจสอบการเปลี่ยนแปลงของเครื่องจักรที่เลือก
# ถ้าเลือกเครื่องจักรใหม่ ให้โหลดประวัติการแชทใหม่
if st.session_state.get("current_machine") != selected_machine:
    st.session_state.messages = load_chat_history(selected_machine)
    st.session_state["current_machine"] = selected_machine

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
        # Send message to n8n webhook
        payload = {"message": prompt, "machine": selected_machine} # เพิ่ม machine name ใน payload
        headers = {"Content-Type": "application/json"}
        response = requests.post(N8N_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()

        # Get n8n's response
        n8n_response_data = response.json()
        n8n_message = n8n_response_data.get("reply", "No reply received from n8n.")

        # Add n8n's response to chat history
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

    # Save the updated chat history to file and rerun
    save_chat_history(selected_machine, st.session_state.messages)
    st.rerun()


