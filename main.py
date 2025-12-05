import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Main Entry Point
# This file handles the navigation to different pages.

# Page Configuration
st.set_page_config(page_title="Sam - AI Assistant", page_icon="🤖", layout="centered")

from app.auth import sign_in, sign_up, sign_out, get_profile, update_profile, restore_session

# Initialize session state for authentication
if "session" not in st.session_state:
    st.session_state["session"] = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# Restore session on every rerun
restore_session()

def login_page_func():
    st.title("Welcome Back")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign In", type="primary")
            
            if submitted:
                response = sign_in(email, password)
                if hasattr(response, "user") and response.user and response.session:
                    st.session_state.authenticated = True
                    st.session_state.user = response.user
                    st.session_state.access_token = response.session.access_token
                    st.rerun()
                elif isinstance(response, dict) and "error" in response:
                    st.error(response["error"])
                else:
                    st.error("Login failed. Please check your credentials.")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Sign Up")
            
            if submitted:
                response = sign_up(new_email, new_password)
                if hasattr(response, "user") and response.user:
                    if response.session:
                        # Auto-login if session is returned (email confirmation disabled)
                        st.session_state.authenticated = True
                        st.session_state.user = response.user
                        st.session_state.access_token = response.session.access_token
                        st.rerun()
                    else:
                        st.success("Sign up successful! Please check your email to confirm your account, then sign in.")
                elif isinstance(response, dict) and "error" in response:
                    st.error(response["error"])
                else:
                    st.error("Sign up failed.")

# Define pages
login_page = st.Page(login_page_func, title="Login", icon="🔒")
chat_page = st.Page("app/pages/chat.py", title="Chat", icon="💬")

if st.session_state.authenticated:
    # Check for User Profile (Onboarding)
    profile = get_profile(st.session_state.user.id)
    
    if not profile:
        # Onboarding Flow
        st.title("Welcome! Let's get to know you.")
        with st.form("onboarding_form"):
            full_name = st.text_input("What should we call you?")
            submitted = st.form_submit_button("Save & Continue", type="primary")
            
            if submitted:
                if full_name:
                    update_profile(st.session_state.user.id, full_name)
                    st.rerun()
                else:
                    st.error("Please enter your name.")
        # Stop execution here to prevent showing the rest of the app
        st.stop()

    # Sidebar with user info and logout
    with st.sidebar:
        display_name = profile.get("full_name") if profile else st.session_state.user.email
        st.write(f"Hi, {display_name}!")
        if st.button("Sign Out"):
            sign_out()
            st.rerun()
            
    pg = st.navigation([chat_page])
else:
    pg = st.navigation([login_page])

# Run the selected page
pg.run()
