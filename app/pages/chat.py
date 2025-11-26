import streamlit as st
from app.utils import load_css, invoke_n8n_webhook
from app.auth import get_user_sessions, create_session, get_session_messages, save_message, update_session_title, delete_session

# Load Custom CSS
load_css()

# Header
st.title("Sam")
st.caption("Company Insights & Career Guidance Assistant")

# Initialize Session State
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar - Chat History
with st.sidebar:
    st.title("Chat History")
    
    if st.button("+ New Chat", use_container_width=True):
        new_session = create_session()
        if new_session:
            st.session_state.current_session_id = new_session["id"]
            st.rerun()

    st.markdown("---")
    
    sessions = get_user_sessions()
    
    # Initialize editing state if not present
    if "editing_session_id" not in st.session_state:
        st.session_state.editing_session_id = None

    def save_rename(session_id):
        new_title = st.session_state[f"input_{session_id}"]
        if new_title:
            update_session_title(session_id, new_title)
        st.session_state.editing_session_id = None
        # No need to rerun here, on_change handles the value update, and the loop will re-render with new title next run
        # But to show the change immediately, we might need a rerun or just let Streamlit handle it.
        # Actually, on_change runs BEFORE the script rerun. So the next rerun will have the updated data.

    for session in sessions:
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            if st.session_state.editing_session_id == session["id"]:
                # Edit Mode: Show Text Input with auto-save on blur/enter
                st.text_input(
                    "Rename", 
                    value=session.get("title", "Untitled Chat"), 
                    key=f"input_{session['id']}", 
                    label_visibility="collapsed",
                    on_change=save_rename,
                    args=(session["id"],)
                )
            else:
                # Normal Mode: Show Session Button
                if st.button(session.get("title", "Untitled Chat"), key=f"btn_{session['id']}", use_container_width=True):
                    st.session_state.current_session_id = session["id"]
                    st.rerun()
        
        with col2:
            # Three-dot menu
            with st.popover("⋮", use_container_width=True):
                if st.button("✏️ Rename", key=f"edit_{session['id']}", use_container_width=True):
                    st.session_state.editing_session_id = session["id"]
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{session['id']}", use_container_width=True):
                    if delete_session(session["id"]):
                        if st.session_state.current_session_id == session["id"]:
                            st.session_state.current_session_id = None
                        st.rerun()

# Main Chat Area
if not st.session_state.current_session_id:
    # If no session selected, create one automatically or show welcome
    if not sessions:
        new_session = create_session()
        if new_session:
            st.session_state.current_session_id = new_session["id"]
            st.rerun()
    else:
        st.session_state.current_session_id = sessions[0]["id"]
        st.rerun()

# Load messages for current session
messages = get_session_messages(st.session_state.current_session_id)

# Display Chat History
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask me about company roles, salaries, or interview tips..."):
    # Save user message
    save_message(st.session_state.current_session_id, "user", prompt)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = invoke_n8n_webhook(prompt, st.session_state.current_session_id)
            st.markdown(response_text)
    
    # Save assistant message
    save_message(st.session_state.current_session_id, "assistant", response_text)
    
    # Smart Session Naming: Rename if it's the first interaction
    # If we have exactly 2 messages (1 user, 1 assistant), it's time to name the session
    try:
        if len(messages) == 0: # messages list is loaded at start, so it doesn't include the 2 just added
             # Wait, messages is loaded at line 47. We just added 2 messages.
             # We should re-fetch or just check if the current title is "New Chat"
             pass
        
        # Let's just check the title directly from DB or session list
        current_title = "New Chat"
        for s in sessions:
            if s["id"] == st.session_state.current_session_id:
                current_title = s.get("title", "New Chat")
                break
        
        if current_title == "New Chat" or current_title == "Untitled Chat":
            # Generate title from prompt
            new_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
            update_session_title(st.session_state.current_session_id, new_title)
            st.rerun()
    except Exception:
        pass

    # Rerun to update history
    st.rerun()
