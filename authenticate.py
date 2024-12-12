import hashlib
def authenticate_user(connection, username, password):
    cursor = connection.cursor(dictionary=True)  # Results as a dictionary
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    query = """
    SELECT username, password, is_admin, user_type  -- Include user_type in query
    FROM users
    WHERE username = %s
    """
    cursor.execute(query, (username,))
    user = cursor.fetchone()  # Fetch user data as a dictionary
    cursor.close()

    # Validate password
    if user and user["password"] == hashed_password:
        return user
    return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()