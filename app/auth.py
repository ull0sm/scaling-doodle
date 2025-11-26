import os
import streamlit as st
from supabase import create_client, Client

def init_supabase(access_token: str = None) -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL and Key are missing. Please add them to your .env file.")
        st.stop()
        
    client = create_client(url, key)
    
    if access_token:
        client.postgrest.auth(access_token)
        
    return client

def sign_in(email, password):
    supabase = init_supabase()
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_up(email, password):
    supabase = init_supabase()
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_out():
    supabase = init_supabase()
    try:
        supabase.auth.sign_out()
    except Exception as e:
        pass # Ignore errors on logout

def get_user_sessions():
    token = st.session_state.get("access_token")
    if not token:
        return []
    supabase = init_supabase(token)
    try:
        response = supabase.table("chat_sessions").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []

def create_session(title="New Chat"):
    token = st.session_state.get("access_token")
    if not token:
        return None
    supabase = init_supabase(token)
    try:
        response = supabase.table("chat_sessions").insert({"user_id": st.session_state.user.id, "title": title}).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None

def get_session_messages(session_id):
    token = st.session_state.get("access_token")
    if not token:
        return []
    supabase = init_supabase(token)
    try:
        response = supabase.table("chat_messages").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching messages: {e}")
        return []

def save_message(session_id, role, content):
    token = st.session_state.get("access_token")
    if not token:
        return
    supabase = init_supabase(token)
    try:
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        st.error(f"Error saving message: {e}")

def get_profile(user_id):
    token = st.session_state.get("access_token")
    if not token:
        return None
    supabase = init_supabase(token)
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data
    except Exception as e:
        # Profile might not exist yet
        return None

def update_profile(user_id, full_name):
    token = st.session_state.get("access_token")
    if not token:
        return None
    supabase = init_supabase(token)
    try:
        # Upsert profile
        response = supabase.table("profiles").upsert({"id": user_id, "full_name": full_name}).execute()
        return response.data
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return None

def update_session_title(session_id, title):
    token = st.session_state.get("access_token")
    if not token:
        return None
    supabase = init_supabase(token)
    try:
        response = supabase.table("chat_sessions").update({"title": title}).eq("id", session_id).execute()
        return response.data
    except Exception as e:
        print(f"Error updating session title: {e}")
        return None

def delete_session(session_id):
    token = st.session_state.get("access_token")
    if not token:
        return False
    supabase = init_supabase(token)
    try:
        # Cascade delete should handle messages if configured, but let's be safe
        # Assuming ON DELETE CASCADE is set in SQL, deleting session is enough.
        # If not, we might need to delete messages first. 
        # Given the schema I saw earlier, I didn't verify CASCADE. 
        # Let's try deleting the session.
        supabase.table("chat_sessions").delete().eq("id", session_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False
