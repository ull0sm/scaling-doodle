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

    for session in sessions:
        # Layout: [Session Name/Input] [Edit] [Delete]
        col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
        
        with col1:
            if st.session_state.editing_session_id == session["id"]:
                # Edit Mode: Show Text Input
                new_title = st.text_input("Rename", value=session.get("title", "Untitled Chat"), key=f"input_{session['id']}", label_visibility="collapsed")
                if new_title != session.get("title", "Untitled Chat"):
                    if st.button("💾", key=f"save_{session['id']}", help="Save Name"):
                        update_session_title(session["id"], new_title)
                        st.session_state.editing_session_id = None
                        st.rerun()
            else:
                # Normal Mode: Show Session Button
                if st.button(session.get("title", "Untitled Chat"), key=f"btn_{session['id']}", use_container_width=True):
                    st.session_state.current_session_id = session["id"]
                    st.rerun()
        
        with col2:
            if st.session_state.editing_session_id == session["id"]:
                 if st.button("❌", key=f"cancel_{session['id']}", help="Cancel"):
                    st.session_state.editing_session_id = None
                    st.rerun()
            else:
                if st.button("✏️", key=f"edit_{session['id']}", help="Rename Chat"):
                    st.session_state.editing_session_id = session["id"]
                    st.rerun()

        with col3:
             if st.button("🗑️", key=f"del_{session['id']}", help="Delete Chat"):
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
