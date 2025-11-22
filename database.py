"""
Database helper functions for CRUD operations on Supabase tables.
"""
from typing import List, Dict, Any, Optional
from supabase import Client


def create_session(supabase: Client, user_id: str, title: str = "New Chat") -> Optional[str]:
    """
    Create a new chat session.
    Returns session_id if successful.
    """
    try:
        result = supabase.table("sessions").insert({
            "user_id": user_id,
            "title": title
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
    except Exception as e:
        print(f"Error creating session: {e}")
    return None


def get_user_sessions(supabase: Client, user_id: str) -> List[Dict[str, Any]]:
    """
    Get all sessions for a user, ordered by most recent first.
    """
    try:
        result = supabase.table("sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting user sessions: {e}")
        return []


def get_session_messages(supabase: Client, session_id: str) -> List[Dict[str, Any]]:
    """
    Get all messages for a session, ordered chronologically.
    """
    try:
        result = supabase.table("messages") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting session messages: {e}")
        return []


def insert_message(supabase: Client, session_id: str, role: str, content: str) -> Optional[str]:
    """
    Insert a new message into a session.
    Returns message_id if successful.
    """
    try:
        result = supabase.table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
    except Exception as e:
        print(f"Error inserting message: {e}")
    return None


def update_profile_summary(supabase: Client, user_id: str, summary: str) -> bool:
    """
    Update user's profile summary.
    """
    try:
        result = supabase.table("users") \
            .update({"profile_summary": summary}) \
            .eq("id", user_id) \
            .execute()
        
        return result.data is not None
    except Exception as e:
        print(f"Error updating profile summary: {e}")
        return False


def get_profile_summary(supabase: Client, user_id: str) -> Optional[str]:
    """
    Get user's profile summary.
    """
    try:
        result = supabase.table("users") \
            .select("profile_summary") \
            .eq("id", user_id) \
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get("profile_summary")
    except Exception as e:
        print(f"Error getting profile summary: {e}")
    return None


def count_user_messages_in_session(supabase: Client, session_id: str) -> int:
    """
    Count number of user messages in a session.
    """
    try:
        result = supabase.table("messages") \
            .select("id", count="exact") \
            .eq("session_id", session_id) \
            .eq("role", "user") \
            .execute()
        
        return result.count if result.count else 0
    except Exception as e:
        print(f"Error counting messages: {e}")
        return 0


def delete_session(supabase: Client, session_id: str) -> bool:
    """
    Delete a session (cascade deletes messages).
    """
    try:
        result = supabase.table("sessions") \
            .delete() \
            .eq("id", session_id) \
            .execute()
        
        return True
    except Exception as e:
        print(f"Error deleting session: {e}")
        return False


def update_session_title(supabase: Client, session_id: str, title: str) -> bool:
    """
    Update session title.
    """
    try:
        result = supabase.table("sessions") \
            .update({"title": title}) \
            .eq("id", session_id) \
            .execute()
        
        return result.data is not None
    except Exception as e:
        print(f"Error updating session title: {e}")
        return False
