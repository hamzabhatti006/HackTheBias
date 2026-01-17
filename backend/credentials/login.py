import mysql.connector
import bcrypt
import json

# Data base Configuration: Use person credintials 
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Omar2011",
    "database": "silent_speak_db",
    "port": 3306
}

# Login logic: Take username and password from frontend and return login status and message
def login_user(username: str, password: str):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT password_hash, email_verified
        FROM users
        WHERE username = %s
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if not result:
            return {
                "login": False,
                "message": "User does not exist"
            }

        stored_hash, email_verified = result

        if not email_verified:
            return {
                "login": False,
                "message": "Email not verified"
            }

        if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return {
                "login": False,
                "message": "Incorrect password"
            }

        return {
            "login": True,
            "message": "Login successful"
        }

    except mysql.connector.Error:
        return {
            "login": False,
            "message": "Internal server error"
        }

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


# TEST RUNNER (TEMPORARY) ****
if __name__ == "__main__":
    print("=== LOGIN TEST ===")
    username = input("Username: ")
    password = input("Password: ")

    response = login_user(username, password)

    print("\nRESPONSE:")
    print(json.dumps(response, indent=2))