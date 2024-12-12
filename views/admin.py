import streamlit as st
from users.manage import manage_user
from AdminControl.Operations import table_operations
def admin_panel(connection):
    st.title("Admin Panel")

    menu = ["Manage Users", "Manage Tables"]
    choice = st.sidebar.selectbox("What do you want to do today?", menu)
    
    if(choice == "Manage Users"):
        manage_user(connection)
    else:
        table_operations(connection)
