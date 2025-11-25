import streamlit as st

# Main Entry Point
# This file handles the navigation to different pages.

# Page Configuration
st.set_page_config(page_title="Sam - AI Assistant", page_icon="🤖", layout="centered")

# Define pages
chat_page = st.Page("app/pages/chat.py", title="Chat", icon="💬")

# Navigation Setup
pg = st.navigation([chat_page])

# Run the selected page
pg.run()
