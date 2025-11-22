"""
Simple Chatbot Application - Main Entry Point
Redirects to the chat page at /app/chat
"""
import streamlit as st

# Page config
st.set_page_config(
    page_title="Simple Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirect to chat page
st.markdown("""
# Welcome to Simple Chatbot 🤖

This is a minimal chatbot application with n8n integration.

Please navigate to the chat page to start chatting with Sam.
""")

st.markdown("### 👉 [Go to Chat Page](/app/chat)")

st.markdown("---")

st.markdown("""
### Features
- 💬 ChatGPT-like interface
- 🤖 Powered by n8n AI Agent workflow
- 🎨 Clean dark theme
- ⚡ Fast and simple

### Quick Start
1. Ensure your `.env` file is configured with `N8N_WEBHOOK_URL`
2. Navigate to the chat page using the link above
3. Start chatting with Sam!
""")
