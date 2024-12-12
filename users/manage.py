import streamlit as st
from authenticate import hash_password
import mysql.connector
def manage_user(connection):
            # View non-admin users and allow updates
        st.header("Manage Users")
        

        # Fetch all non-admin users
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE is_admin = FALSE")
        users = cursor.fetchall()
        cursor.close()
        
        # Display list of non-admin users
        if users:
            selected_user_id = st.selectbox("Select a User to Edit", [user[1] for user in users])
            if selected_user_id:
                # Get the user details based on the selection
                selected_user = next(user for user in users if user[1] == selected_user_id)
                user_id, username, email, is_admin = selected_user
                
                # Display current details
                st.write(f"Username: {username}")
                st.write(f"Email: {email}")
                
                # Edit user details
                new_username = st.text_input("New Username", value=username)
                new_email = st.text_input("New Email", value=email)
                new_password = st.text_input("New Password", type="password")
                new_is_admin = st.checkbox("Grant Admin Privileges", value=is_admin)
                
                if st.button("Update User Details"):
                    try:
                        cursor = connection.cursor()
                        
                        # If a new password is provided, hash it
                        if new_password:
                            hashed_password = hash_password(new_password)
                            cursor.execute("""
                                UPDATE users
                                SET username = %s, email = %s, is_admin = %s, password = %s
                                WHERE id = %s
                            """, (new_username, new_email, new_is_admin, hashed_password, user_id))
                        else:
                            # If no password change, just update the other fields
                            cursor.execute("""
                                UPDATE users
                                SET username = %s, email = %s, is_admin = %s
                                WHERE id = %s
                            """, (new_username, new_email, new_is_admin, user_id))
                        
                        connection.commit()
                        cursor.close()
                        st.success("User details updated successfully!")
                    except mysql.connector.Error as e:
                        st.error(f"Error updating user details: {e}")
                if st.button("Delete User"):
                    try:
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                        connection.commit()
                        cursor.close()
                        st.success(f"User '{username}' deleted successfully!")
                    except mysql.connector.Error as e:
                        st.error(f"Error deleting user: {e}")
        else:
            st.write("No non-admin users found.")
