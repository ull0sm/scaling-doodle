import streamlit as st
from app.utils import load_css, invoke_n8n_webhook

# Page Configuration (Handled in main.py)
# st.set_page_config(page_title="Sam - AI Assistant", page_icon="🤖", layout="centered")

# Load Custom CSS
load_css()

# Header
st.title("Sam")
st.caption("Company Insights & Career Guidance Assistant")

import uuid

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask me about company roles, salaries, or interview tips..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = invoke_n8n_webhook(prompt, st.session_state.session_id)
            st.markdown(response_text)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
