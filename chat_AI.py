import streamlit as st
import json
import os

# --- Page Configurations ---

st.set_page_config(page_title="n8n Chatbot App", layout="centered")
# --- Sidebar for Navigation ---
# สร้างเมนูทางด้านซ้าย (Sidebar)
Data = st.Page(page=r'C:\Users\papeko14\Documents\fastwork\สอนไพธอน\mentor\2025-07-29\views\Table_Data.py',title='Data', icon='📅')
chat_bot = st.Page(page=r'C:\Users\papeko14\Documents\fastwork\สอนไพธอน\mentor\2025-07-29\views\Chat_page.py',title='Chat_bot', icon='🤖')
graph = st.Page(page=r'C:\Users\papeko14\Documents\fastwork\สอนไพธอน\mentor\2025-07-29\views\Graph_data.py',title='Chat_bot', icon='📊')
pg = st.navigation(
        pages=[chat_bot,Data,graph]
    )
pg.run()
