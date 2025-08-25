import streamlit as st
import json
import os

# --- Page Configurations ---

st.set_page_config(page_title="n8n Chatbot App", layout="centered")
# --- Sidebar for Navigation ---
# สร้างเมนูทางด้านซ้าย (Sidebar)
Data = st.Page(page='Table_Data.py',title='Data', icon='📅')
chat_bot = st.Page(page='Chat_page.py',title='Chat_bot', icon='🤖')
chat_zone = st.Page(page='Chat_page_zone.py',title='Chat_bot_zone',icon='🤖')
graph = st.Page(page=r'Graph_data.py',title='Data Visualization', icon='📊')
test_db = st.Page(page=r'test_db.py',title='Data base', icon='📊')
pg = st.navigation(
        pages=[test_db,chat_zone,Data,graph]
    )
pg.run()













