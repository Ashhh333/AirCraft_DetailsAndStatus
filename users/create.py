import mysql.connector
import streamlit as st
from authenticate import hash_password
def create_user(connection, username, password, email, is_admin=False):
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, email, is_admin) VALUES (%s, %s, %s, %s)", 
                      (username, hashed_password, email, is_admin))
        connection.commit()
        cursor.close()
        return True
    except mysql.connector.Error as e:
        if e.errno == 1062:
            st.error("Username or email already exists!")
        else:
            st.error(f"Error creating user: {e}")
        return False
