import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def load_css():
    """
    Injects custom CSS for a premium, 'Slate Minimal' professional feel.
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

        /* Hide Streamlit Branding but keep Sidebar Toggle */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {
            visibility: visible !important;
            background-color: transparent !important;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
            z-index: 1;
        }
        
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

        /* Buttons */
        .stButton button {
            background: linear-gradient(to right, #4f46e5, #7c3aed);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }

        /* Sidebar Buttons (Session List) */
        [data-testid="stSidebar"] .stButton button {
            background: transparent;
            border: none; /* Remove border for cleaner look */
            text-align: left;
            justify-content: flex-start;
            padding-left: 0.5rem;
            font-weight: 400;
            color: #cbd5e1;
            transition: background-color 0.2s, color 0.2s;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255, 255, 255, 0.05);
            color: white;
        }

        [data-testid="stSidebar"] .stButton button:focus {
            color: #818cf8;
        }

        /* Sidebar Column Spacing */
        [data-testid="stSidebar"] [data-testid="column"] {
            padding-left: 0 !important;
            padding-right: 0 !important;
            gap: 0 !important;
        }

        /* Compact Action Buttons (Edit/Delete) */
        [data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button,
        [data-testid="stSidebar"] [data-testid="column"]:nth-child(3) button {
            padding: 0px 4px !important; /* Minimal padding */
            border: none;
            background: transparent;
            color: #64748b; /* Muted color */
            min-height: auto;
            height: 36px; /* Match row height */
            line-height: 1;
        }

        [data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button:hover,
        [data-testid="stSidebar"] [data-testid="column"]:nth-child(3) button:hover {
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(30, 41, 59, 0.5);
            padding: 4px;
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 6px;
            color: #94a3b8;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(79, 70, 229, 0.2);
            color: #818cf8;
        }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            /* Increase touch targets for sidebar buttons */
            [data-testid="stSidebar"] [data-testid="column"] button {
                padding: 0.5rem 0.75rem !important; /* Larger padding */
                min-height: 44px; /* Minimum touch target size */
            }
            
            /* Stack sidebar columns if needed, or just give them more breathing room */
            [data-testid="stSidebar"] [data-testid="column"] {
                margin-bottom: 0.25rem;
            }

            /* Adjust main chat padding */
            .stChatMessage {
                padding: 1rem;
            }
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
