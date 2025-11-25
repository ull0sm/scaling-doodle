import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def load_css():
    """
    Injects custom CSS for a premium, 'Slate Minimal' professional feel.
    Fixes visibility issues by forcing colors and removing fragile selectors.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* Force Light Mode Colors for Consistency */
        :root {
            --background-color: #f8fafc; /* Slate-50 */
            --text-color: #334155; /* Slate-700 */
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
        }

        /* General App Styling */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
        }
        
        /* Force text color on all elements to avoid Dark Mode conflicts */
        .stApp p, .stApp div, .stApp span, .stApp h1, .stApp h2, .stApp h3 {
            color: var(--text-color) !important;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Chat Input Styling */
        .stChatInputContainer {
            padding-bottom: 2rem;
            background-color: transparent;
        }
        
        .stChatInputContainer textarea {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        /* Chat Message Styling - Unified Card Style */
        .stChatMessage {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        /* Avatar Styling */
        .stChatMessage .stAvatar {
            background-color: #f1f5f9; /* Slate-100 */
            border: 1px solid #e2e8f0;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #334155 !important;
        }
        
        </style>
    """, unsafe_allow_html=True)

def invoke_n8n_webhook(message: str, session_id: str) -> str:
    """
    Sends the user message to the n8n webhook and returns the response.
    Includes sessionId for conversation memory.
    """
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if not webhook_url:
        return "Error: N8N_WEBHOOK_URL not configured."

    try:
        # Payload with message and session ID as requested
        # We include both sessionId (for memory) and messageId (as requested)
        import uuid
        payload = {
            "message": message,
            "sessionId": session_id,
            "messageId": str(uuid.uuid4())
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # The user's workflow "Respond to Webhook" node sends:
        # { "reply": "{{ $json.output }}" }
        return data.get("reply", "No reply received from agent.")

    except requests.exceptions.RequestException as e:
        return f"Error communicating with agent: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
