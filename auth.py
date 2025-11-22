"""
Authentication module for Supabase Google OAuth.
"""
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any


def init_supabase(url: str, key: str) -> Client:
    """Initialize Supabase client."""
    return create_client(url, key)


def get_auth_url(supabase: Client) -> str:
    """Get Google OAuth URL from Supabase."""
    # Supabase handles OAuth redirect automatically
    # The user needs to configure Google OAuth in Supabase dashboard
    return supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": st.get_option("browser.serverAddress") or "http://localhost:8501"
        }
    })


def get_current_user(supabase: Client) -> Optional[Dict[str, Any]]:
    """Get currently authenticated user."""
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            return {
                "id": session.user.id,
                "email": session.user.email,
                "name": session.user.user_metadata.get("full_name", ""),
                "avatar_url": session.user.user_metadata.get("avatar_url", "")
            }
    except Exception as e:
        print(f"Error getting current user: {e}")
    return None


def sign_out(supabase: Client) -> None:
    """Sign out current user."""
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Error signing out: {e}")


def ensure_user_exists(supabase: Client, user_data: Dict[str, Any]) -> Optional[str]:
    """
    Ensure user exists in database, create if not.
    Returns user_id if successful.
    """
    try:
        # Check if user exists
        result = supabase.table("users").select("id").eq("email", user_data["email"]).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        # Create new user
        insert_result = supabase.table("users").insert({
            "email": user_data["email"],
            "name": user_data.get("name", ""),
            "avatar_url": user_data.get("avatar_url", "")
        }).execute()
        
        if insert_result.data and len(insert_result.data) > 0:
            return insert_result.data[0]["id"]
    except Exception as e:
        print(f"Error ensuring user exists: {e}")
    return None
