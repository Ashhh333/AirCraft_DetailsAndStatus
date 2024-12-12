import mysql.connector
import streamlit as st
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            user='root',
            password='ayushff@123',
            host='localhost',
            database='aircraft_details_n_status'
        )
        cursor = connection.cursor()
        # Create users table with is_admin field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                user_type VARCHAR(50) NOT NULL DEFAULT 'regular'
            )
        """)
        connection.commit()
        cursor.close()
        return connection
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None