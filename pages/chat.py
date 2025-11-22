"""
Simple Chatbot - Chat Page
ChatGPT-like interface with n8n webhook integration
"""
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import uuid
import time

# Load environment variables
load_dotenv()

# Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
try:
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
except (ValueError, TypeError):
    REQUEST_TIMEOUT = 30

# Page config
st.set_page_config(
    page_title="Chat with Sam",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #121212;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Message containers */
    .user-message {
        background-color: #2d2d2d;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 4px solid #10a37f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .assistant-message {
        background-color: #1e1e1e;
        padding: 16px 20px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 4px solid #6b6b6b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Text colors */
    .user-message p, .assistant-message p {
        color: #e0e0e0;
        margin: 0;
        line-height: 1.6;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 2px solid #3d3d3d;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10a37f;
    }
    
    /* Send button */
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #0d8c6c;
        box-shadow: 0 4px 8px rgba(16,163,127,0.3);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #10a37f !important;
    }
    
    /* Message labels */
    .message-label {
        font-weight: 600;
        margin-bottom: 8px;
        color: #b0b0b0;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


def call_n8n_webhook(message: str) -> str:
    """
    Call the n8n webhook and return the response.
    
    Args:
        message: User's message text
        
    Returns:
        Assistant's reply text
    """
    if not N8N_WEBHOOK_URL:
        return "⚠️ N8N_WEBHOOK_URL not configured. Please set it in your .env file."
    
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            # Try to extract reply from various possible fields
            reply = data.get("reply") or data.get("output") or data.get("text")
            
            if reply:
                return reply
            else:
                # Log available fields for debugging
                available_fields = list(data.keys()) if isinstance(data, dict) else []
                return f"⚠️ No reply field found in n8n response. Available fields: {available_fields}"
        else:
            return f"⚠️ n8n webhook returned status code {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. The n8n workflow is taking too long. Try increasing REQUEST_TIMEOUT in .env."
    except requests.exceptions.ConnectionError:
        return "⚠️ Could not connect to n8n webhook. Please check your N8N_WEBHOOK_URL."
    except Exception as e:
        return f"⚠️ Error calling n8n webhook: {str(e)}"


def render_message(role: str, content: str):
    """Render a single message with appropriate styling."""
    if role == "user":
        st.markdown(
            f'<div class="user-message">'
            f'<div class="message-label">You</div>'
            f'<p>{content}</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    elif role == "assistant":
        st.markdown(
            f'<div class="assistant-message">'
            f'<div class="message-label">Sam</div>'
            f'<p>{content}</p>'
            f'</div>',
            unsafe_allow_html=True
        )


def main():
    """Main application logic."""
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown("# 💬 Chat with Sam")
    st.markdown("Your AI-powered Company Insights & Career Guidance Assistant")
    st.markdown("---")
    
    # Check configuration
    if not N8N_WEBHOOK_URL:
        st.error("⚠️ N8N_WEBHOOK_URL is not configured. Please set it in your .env file.")
        st.markdown("""
        **Setup Instructions:**
        1. Copy `.env.example` to `.env`
        2. Set your n8n webhook URL in the `.env` file
        3. Restart the application
        """)
        st.stop()
    
    # Display chat messages
    chat_area = st.container()
    with chat_area:
        if not st.session_state.messages:
            # Welcome message
            render_message(
                "assistant",
                "Hello! I'm Sam, your Company Insights & Career Guidance Assistant. "
                "I can help you with company information, interview preparation, job search strategies, "
                "and career development. How can I assist you today?"
            )
        else:
            # Display all messages
            for msg in st.session_state.messages:
                render_message(msg["role"], msg["content"])
    
    # Spacer
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    # Input area at the bottom
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Ask me about companies, careers, interviews, salaries..."
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True, type="primary")
    
    # Handle message submission
    if send_button and user_input:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Show loading state
        with st.spinner("Sam is thinking..."):
            # Call n8n webhook
            assistant_reply = call_n8n_webhook(user_input)
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        # Rerun to display new messages
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### 📋 Chat Session")
        st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
        st.markdown("---")
        
        st.markdown("### 🔄 Actions")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🆕 New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Sam** is powered by:
        - 🤖 n8n AI Agent
        - 🔍 RAG with Pinecone
        - 🌐 Web Search
        - 🧠 Google Gemini
        """)
        
        st.markdown("---")
        st.caption(f"Messages: {len(st.session_state.messages)}")


if __name__ == "__main__":
    main()
