import mysql.connector

# database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Omar2011",
    "database": "silent_speak_db",
    "port": 3306
}

# Verify email function
def verify_email(username: str, code: str):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Fetch stored verification code
        query = """
        SELECT email_verification_code, email_verified
        FROM users
        WHERE username = %s
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if not result:
            return False, "User does not exist"

        stored_code, is_verified = result

        if is_verified:
            return False, "Email already verified"

        if stored_code != code:
            return False, "Invalid verification code"

        # Mark email as verified and clear the code
        update_query = """
        UPDATE users
        SET email_verified = TRUE,
            email_verification_code = NULL
        WHERE username = %s
        """
        cursor.execute(update_query, (username,))
        connection.commit()

        return True, "Email verified successfully"

    except mysql.connector.Error:
        return False, "Database error during verification"

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


# test
if __name__ == "__main__":
    print("=== EMAIL VERIFICATION ===")
    username = input("Username: ")
    code = input("Verification code: ")

    success, message = verify_email(username, code)

    print("\nRESULT:")
    print("Success:", success)
    print("Message:", message)