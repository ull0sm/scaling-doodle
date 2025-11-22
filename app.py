"""
Company Insight Chat UI - Streamlit Application
Dark-mode chat interface with Supabase authentication and n8n integration.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from auth import init_supabase, get_current_user, ensure_user_exists, sign_out
from database import (
    create_session, get_user_sessions, get_session_messages,
    insert_message, update_profile_summary, get_profile_summary,
    count_user_messages_in_session
)
from n8n_client import call_n8n_webhook
from summarizer import (
    generate_simple_summary, should_update_summary,
    get_recent_user_messages
)

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
PROFILE_SUMMARY_THRESHOLD = int(os.getenv("PROFILE_SUMMARY_MESSAGE_THRESHOLD", "10"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Dark theme styling
DARK_THEME_CSS = """
<style>
    /* Main background */
    .stApp {
        background-color: #121212;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
    }
    
    /* Message containers */
    .user-message {
        background-color: #2d2d2d;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #10a37f;
    }
    
    .assistant-message {
        background-color: #1e1e1e;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #6b6b6b;
    }
    
    /* Text colors */
    .user-message p, .assistant-message p {
        color: #e0e0e0;
        margin: 0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0d8c6c;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3d3d3d;
        border-radius: 6px;
    }
    
    /* Session items */
    .session-item {
        background-color: #2d2d2d;
        padding: 10px;
        border-radius: 6px;
        margin: 5px 0;
        cursor: pointer;
        border: 1px solid #3d3d3d;
    }
    
    .session-item:hover {
        background-color: #353535;
        border-color: #10a37f;
    }
    
    .session-item-active {
        background-color: #10a37f;
        color: white;
    }
</style>
"""


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sessions" not in st.session_state:
        st.session_state.sessions = []


def render_message(role: str, content: str):
    """Render a single message with appropriate styling."""
    if role == "user":
        st.markdown(f'<div class="user-message"><p><strong>You:</strong> {content}</p></div>', unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f'<div class="assistant-message"><p><strong>Sam:</strong> {content}</p></div>', unsafe_allow_html=True)


def load_session_messages(supabase, session_id: str):
    """Load messages for the current session."""
    messages = get_session_messages(supabase, session_id)
    st.session_state.messages = messages


def send_message(supabase, user_input: str):
    """Handle sending a message and receiving response."""
    if not user_input.strip():
        return
    
    session_id = st.session_state.current_session_id
    user_id = st.session_state.user_id
    
    # Insert user message
    insert_message(supabase, session_id, "user", user_input)
    
    # Get profile summary for context
    profile_summary = get_profile_summary(supabase, user_id)
    
    # Show loading state
    with st.spinner("Sam is thinking..."):
        # Call n8n webhook
        response = call_n8n_webhook(
            N8N_WEBHOOK_URL,
            user_id,
            session_id,
            user_input,
            profile_summary,
            REQUEST_TIMEOUT
        )
    
    # Insert assistant response
    assistant_reply = response.get("reply", "I cannot find this in the available resources.")
    insert_message(supabase, session_id, "assistant", assistant_reply)
    
    # Check if we should update profile summary
    user_msg_count = count_user_messages_in_session(supabase, session_id)
    if should_update_summary(user_msg_count, PROFILE_SUMMARY_THRESHOLD):
        # Get recent messages and generate summary
        all_messages = get_session_messages(supabase, session_id)
        recent_user_msgs = get_recent_user_messages(all_messages, limit=12)
        new_summary = generate_simple_summary(recent_user_msgs)
        
        if new_summary:
            update_profile_summary(supabase, user_id, new_summary)
    
    # Reload messages
    load_session_messages(supabase, session_id)


def render_sidebar(supabase):
    """Render the sidebar with session management."""
    with st.sidebar:
        st.markdown("### 💬 Chat Sessions")
        
        # New session button
        if st.button("➕ New Chat", use_container_width=True):
            new_session_id = create_session(supabase, st.session_state.user_id)
            if new_session_id:
                st.session_state.current_session_id = new_session_id
                st.session_state.messages = []
                st.session_state.sessions = get_user_sessions(supabase, st.session_state.user_id)
                st.rerun()
        
        st.markdown("---")
        
        # List existing sessions
        sessions = get_user_sessions(supabase, st.session_state.user_id)
        st.session_state.sessions = sessions
        
        if sessions:
            st.markdown("**Your Chats:**")
            for session in sessions:
                session_id = session["id"]
                title = session.get("title", "New Chat")
                
                # Truncate title if too long
                display_title = title[:30] + "..." if len(title) > 30 else title
                
                # Highlight active session
                is_active = session_id == st.session_state.current_session_id
                button_type = "primary" if is_active else "secondary"
                
                if st.button(
                    f"{'🟢 ' if is_active else '⚪ '}{display_title}",
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    st.session_state.current_session_id = session_id
                    load_session_messages(supabase, session_id)
                    st.rerun()
        else:
            st.info("No chats yet. Start a new one!")
        
        st.markdown("---")
        
        # User info and sign out
        if st.session_state.user:
            st.markdown(f"**👤 {st.session_state.user.get('name', 'User')}**")
            st.caption(st.session_state.user.get('email', ''))
            
            if st.button("🚪 Sign Out", use_container_width=True):
                sign_out(supabase)
                st.session_state.user = None
                st.session_state.user_id = None
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.session_state.sessions = []
                st.rerun()


def main():
    """Main application logic."""
    # Page config
    st.set_page_config(
        page_title="Company Insight Chat",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply dark theme
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Check configuration
    if not SUPABASE_URL or not SUPABASE_KEY or not N8N_WEBHOOK_URL:
        st.error("⚠️ Missing configuration. Please set SUPABASE_URL, SUPABASE_KEY, and N8N_WEBHOOK_URL in .env file.")
        st.stop()
    
    # Initialize Supabase
    supabase = init_supabase(SUPABASE_URL, SUPABASE_KEY)
    
    # Check authentication
    current_user = get_current_user(supabase)
    
    if not current_user:
        # Show login page
        st.markdown("# 💼 Company Insight Chat")
        st.markdown("### Your AI-powered career guidance assistant")
        st.markdown("")
        st.markdown("Sam helps you with:")
        st.markdown("- 🏢 Company information and culture insights")
        st.markdown("- 💼 Placement and interview preparation")
        st.markdown("- 🎯 Job search strategies")
        st.markdown("- 📊 Industry trends and career development")
        st.markdown("")
        
        st.info("👉 Sign in with Google to start chatting with Sam")
        
        # Note: Actual OAuth flow requires Supabase dashboard configuration
        # User needs to enable Google OAuth provider in Supabase
        st.markdown("""
        **To set up authentication:**
        1. Go to your Supabase project dashboard
        2. Navigate to Authentication > Providers
        3. Enable Google provider and configure OAuth
        4. Add your app URL to authorized redirect URLs
        5. Refresh this page and click the sign-in button below
        """)
        
        if st.button("🔐 Sign in with Google", use_container_width=True):
            st.warning("Please configure Google OAuth in your Supabase dashboard first.")
            st.info("After configuration, Supabase will handle the OAuth flow automatically.")
        
        st.stop()
    
    # User is authenticated
    st.session_state.user = current_user
    
    # Ensure user exists in database
    user_id = ensure_user_exists(supabase, current_user)
    if not user_id:
        st.error("Failed to create user record. Please try again.")
        st.stop()
    
    st.session_state.user_id = user_id
    
    # Create first session if none exists
    if not st.session_state.current_session_id:
        sessions = get_user_sessions(supabase, user_id)
        if sessions:
            st.session_state.current_session_id = sessions[0]["id"]
            load_session_messages(supabase, sessions[0]["id"])
        else:
            # Create first session
            new_session_id = create_session(supabase, user_id)
            if new_session_id:
                st.session_state.current_session_id = new_session_id
                st.session_state.messages = []
    
    # Render sidebar
    render_sidebar(supabase)
    
    # Main chat area
    st.markdown("# 💬 Chat with Sam")
    
    if not st.session_state.current_session_id:
        st.info("👈 Create a new chat to get started!")
        st.stop()
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        if st.session_state.messages:
            for msg in st.session_state.messages:
                render_message(msg["role"], msg["content"])
        else:
            st.markdown('<div class="assistant-message"><p><strong>Sam:</strong> Hello! I\'m Sam, your Company Insights & Career Guidance Assistant. How can I help you today?</p></div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Ask me about companies, careers, interviews..."
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Handle message submission
    if send_button or (user_input and user_input != st.session_state.get("last_input", "")):
        if user_input:
            st.session_state.last_input = user_input
            send_message(supabase, user_input)
            st.rerun()


if __name__ == "__main__":
    main()
