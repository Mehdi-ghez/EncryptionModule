USERS = {
    "user1 Binary": {
        "password": "101",  # Login password
    },
    "user2 Numeric": {
        "password": "54321",   # Login password
    },
    "user3 Alphanum": {
        "password": "abD3@",   # Login password
    }
}

def verify_credentials(username, password):
    """Verify if the username and password match"""
    return username in USERS and USERS[username]["password"] == password

def get_user_list():
    """Get list of all usernames"""
    return list(USERS.keys())
