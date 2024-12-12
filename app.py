import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from datetime import datetime
from authenticate import *
from database_connection import connect_to_database
from users.manage import manage_user
from users.create import create_user
from views.admin import *
from views.user import *
from views.manufacturer import *
from AdminControl.Transaction import*
from AdminControl.Operations import*
from login import login_page
from signup import signup_page
from UserSearch import *

def main():
    # Inject custom CSS to increase font sizes globally
   
    # Display logo and company name side by side
    col1, col2 = st.columns([1, 6])  # Adjust column widths as needed
    with col1:
        st.image("logo.png", use_container_width=True)  # Display logo in the first column
    with col2:
        st.title("FlyingMotors Ltd.")  # Display company name in the second column

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    
    if not st.session_state.logged_in:
        menu = ["Login", "Sign Up"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            login_page()
        else:
            signup_page()
    else:
        st.sidebar.success(f"Welcome {st.session_state.username}")

        # Debugging: Show role
        st.write(f"Logged in as: {st.session_state.username} ({st.session_state.user_type})")

        # Role-based menu options
        if st.session_state.is_admin:
            menu = ["View Data", "Admin Panel"]
        elif st.session_state.user_type == "Manufacturer":
            menu = ["Manufacturer Dashboard"]
        else:
            menu = ["Flight Search"]

        choice = st.sidebar.selectbox("Menu", menu)

        # Admin view
        if choice == "Admin Panel" and st.session_state.is_admin:
            mydb = connect_to_database()
            if mydb:
                admin_panel(mydb)
                mydb.close()
        # Manufacturer view
        elif choice == "Manufacturer Dashboard" and st.session_state.user_type == "Manufacturer":
            manufacturer_dashboard()
        # Regular user view
        elif choice == "Flight Search" and st.session_state.user_type == "Regular":
            flight_search_view()
        else:
            user_view()

        # Logout
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.user_type = None
            st.rerun()

if __name__ == "__main__":
    main()
