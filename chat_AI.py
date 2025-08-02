import streamlit as st
import requests
import json
import os
import pandas as pd
import csv

# --- Configuration ---
# URL ของ n8n webhook
N8N_WEBHOOK_URL = "https://rationally-tough-ant.ngrok-free.app/webhook/d8e551ba-6202-4544-be0a-74294ecff821"

# --- File-based Data Persistence ---
# ชื่อไฟล์สำหรับเก็บประวัติการแชท
CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    """ฟังก์ชันสำหรับโหลดประวัติการแชทจากไฟล์ JSON"""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_chat_history(messages):
    """ฟังก์ชันสำหรับบันทึกประวัติการแชทลงในไฟล์ JSON"""
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

def get_data_from_csv(file_path):
    """ฟังก์ชันสำหรับโหลดและทำความสะอาดข้อมูลจากไฟล์ CSV"""
    try:
        # Load CSV with specified encoding to avoid errors
        df = pd.read_csv(file_path, on_bad_lines='skip', engine='python', quoting=csv.QUOTE_NONE, quotechar='"' )
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()
    
    # Identify and rename duplicate columns to make them unique for filtering
    cols = pd.Series(df.columns)
    for dup in df.columns[df.columns.duplicated(keep=False)]:
        cols[df.columns.get_loc(dup)] = [f"{x}_{i}" if i != 0 else x for i, x in enumerate(cols[df.columns.get_loc(dup)])]
    df.columns = cols
    
    return df

# --- Page Configurations ---
st.set_page_config(page_title="n8n Chatbot App", layout="centered")

# --- Sidebar for Navigation ---
# สร้างเมนูทางด้านซ้าย (Sidebar)
with st.sidebar:
    st.title("Main Menu")
    page_selection = st.selectbox(
        "Select a page:",
        ("หน้าแชท", "หน้าข้อมูล", "หน้ากราฟ")
    )
    st.markdown("---")
    st.info("Developed with Streamlit and n8n")

# --- Main Page Content Logic ---
if page_selection == "หน้าแชท":
    # --- Chatbot Page Content ---
    st.title("🤖 Chat with n8n")
    st.write("Type your message and see n8n's response!")

    # Load chat history from file on app startup if it's not already in session_state
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
            # Send message to n8n webhook
            payload = {"message": prompt}
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
        save_chat_history(st.session_state.messages)
        st.rerun()

elif page_selection == "หน้าข้อมูล":
    # --- Data Dashboard Page Content ---
    st.title("📅 Data Show")
    st.info("You can display a data table here.")
    
    # Load and process data
    df = get_data_from_csv('merged_data.csv')
    
    if not df.empty:
        # --- Data Filtering ---
        st.subheader("Filter Data")
        
        # ให้ผู้ใช้เลือกคอลัมน์ที่จะฟิลเตอร์
        column_to_filter = st.selectbox(
            'Select a column to filter:',
            df.columns.tolist()
        )
        
        # ให้ผู้ใช้เลือกค่าที่จะฟิลเตอร์จากคอลัมน์ที่เลือก
        unique_values = ['All'] + list(df[column_to_filter].unique())
        selected_value = st.selectbox(
            f'Select value for {column_to_filter}:',
            unique_values
        )
        
        # Apply filter to the DataFrame
        filtered_df = df.copy()
        if selected_value != 'All':
            filtered_df = filtered_df[filtered_df[column_to_filter] == selected_value]
            
        st.markdown("---")
        
        st.subheader("Filtered Data")
        
        # --- Handling potential serialization issues ---
        # If the filtered DataFrame is still too large, sample it
        if filtered_df.shape[0] > 100:
            st.warning(f"DataFrame is too large to display. Showing a sample of 1000 rows.")
            filtered_df = filtered_df.sample(100)
            
        # Convert all object dtypes to string to avoid serialization errors
        for col in filtered_df.columns:
            if filtered_df[col].dtype == 'object':
                filtered_df[col] = filtered_df[col].astype(str)

        # Display the filtered DataFrame as a table
        st.dataframe(filtered_df)

elif page_selection == "หน้ากราฟ":
    # --- Graph Page Content ---
    st.title("📊 Data Visualization")
    st.write("Welcome to the Data Dashboard!")
    st.info("You can display a graph from your data here.")

    # Load and process data
    df = get_data_from_csv('merged_data.csv')
    
    if not df.empty:
        st.markdown("---")
        st.subheader("Chart Options")

        # Get all column names and numeric column names
        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if numeric_cols:
            # Dropdown for selecting X-axis
            x_axis = st.selectbox("Select X-axis:", all_cols)
            
            # Dropdown for selecting Y-axis
            y_axis = st.selectbox("Select Y-axis:", numeric_cols)
            
            # --- Data Visualization (Graph) ---
            st.subheader(f"Bar Chart: '{y_axis}' by '{x_axis}'")
            
            # Group data by the selected x-axis and plot the sum of the y-axis
            chart_data = df.groupby(x_axis)[y_axis].sum()
            st.bar_chart(chart_data)
        else:
            st.warning("No numeric columns found in the data to plot.")

