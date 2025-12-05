import streamlit as st
from app.utils import load_css, invoke_n8n_webhook
from app.auth import get_user_sessions, create_session, get_session_messages, save_message, update_session_title, delete_session, require_authentication

# Authentication check - ensure user is logged in
require_authentication()

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
        # Check if we need to rename (only if title is default)
        current_title = "New Chat"
        for s in sessions:
            if s["id"] == st.session_state.current_session_id:
                current_title = s.get("title", "New Chat")
                break
        
        # We only rename if it's still the default title and we have just completed the first exchange
        # (messages list was loaded before this turn, so it was empty, now we added 2 messages)
        if (current_title == "New Chat" or current_title == "Untitled Chat") and len(messages) == 0:
            # Generate title from prompt and response
            import uuid
            naming_prompt = (
                f"Generate a very short, concise title (max 5 words) for a chat session that starts with this exchange:\n"
                f"User: {prompt}\n"
                f"AI: {response_text}\n"
                f"Return ONLY the title, no quotes or extra text."
            )
            
            # Use a temporary session ID to avoid polluting the main chat context
            temp_session_id = f"naming-{uuid.uuid4()}"
            
            # Call AI for title
            generated_title = invoke_n8n_webhook(naming_prompt, temp_session_id)
            
            # Clean up title (remove quotes if any, trim)
            new_title = generated_title.strip().strip('"').strip("'")
            
            # Fallback if AI fails or returns something too long/empty
            if not new_title or len(new_title) > 50 or "Error" in new_title:
                 new_title = prompt[:30] + "..." if len(prompt) > 30 else prompt

            update_session_title(st.session_state.current_session_id, new_title)
            st.rerun()
    except Exception as e:
        # Silently fail to simple naming or just keep existing
        print(f"Smart naming failed: {e}")
        pass

    # Rerun to update history
    st.rerun()
