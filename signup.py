import streamlit as st
from database_connection import*
from users.create import create_user

def signup_page():
    st.subheader("Create New Account")
    
    # Input fields for username, password, and email
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    email = st.text_input("Email")

    # Dropdown for user type selection
    user_type = st.selectbox("Select User Type", ["Admin", "Regular", "Manufacturer"])

    # Display a success message if the account was just created
    if st.session_state.get("signup_success", False):
        st.success("Account created successfully! Please login.")
        if st.button("Sign Up Another Account"):  # Option to show signup again
            st.session_state.signup_success = False
            st.rerun()
        # if st.button("Go to Login"):
        #     st.session_state.signup_success = False
        #     st.rerun()
            

    elif st.button("Sign Up"):
        if username and password and email:
            mydb = connect_to_database()
            if mydb:
                # Automatically set `is_admin` based on user type
                is_admin = user_type == "Admin"
                
                # Create the user with the selected user type
                if create_user(mydb, username, password, email, is_admin, user_type):
                    # Set a flag for success
                    st.session_state.signup_success = True
                    st.rerun()  # Reload page to show the success message
                else:
                    st.error("Error creating account. Username or email may already exist.")
                mydb.close()
        else:
            st.warning("Please fill all fields!")