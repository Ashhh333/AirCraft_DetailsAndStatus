import streamlit as st
from database_connection import*
from authenticate import authenticate_user

def login_page():
    st.subheader("Login")

    # Ask for user type
    user_type = st.radio("Select User Type", ("Admin", "Regular", "Manufacturer"))

    # Username and password fields
    username = st.text_input(f"👤 Username for {user_type}")
    password = st.text_input(f"🔑 Password for {user_type}", type="password")

    if st.button("Login"):
        connection = connect_to_database()
        if connection:
            user = authenticate_user(connection, username, password)
            if user:
                # Validate user type matches
                if user["user_type"] == user_type:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.is_admin = user["is_admin"]  # Save admin status
                    st.session_state.user_type = user["user_type"]  # Save user type
                    
                    st.success("Logged in successfully!")
                    st.rerun()  # Reload the app to refresh the UI
                else:
                    st.error(f"Invalid user type for {username}.")
            else:
                st.error("Invalid username or password")
            connection.close()