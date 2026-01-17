import mysql.connector
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database configuration: using your own database credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Omar2011",
    "database": "silent_speak_db",
    "port": 3306
}

# Email configuration: ***DO NOT CHANGE!
SMTP_EMAIL = "boudyattia1@gmail.com"
SMTP_PASSWORD = "ubfncwwclepluqzc"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


# Helper functions -- 

# Encrept password using bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Generate a 6-digit verification code
def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

# Send email with verification code
def send_verification_email(to_email: str, code: str):
    message = MIMEMultipart()
    message["From"] = SMTP_EMAIL
    message["To"] = to_email
    message["Subject"] = "SilentSpeak Email Verification"

    body = f"""
Welcome to SilentSpeak!

Your verification code is:

{code}

Enter this code in the app to verify your email.
"""
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(message)

# Check if username or email already exists
def username_exists(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    return cursor.fetchone() is not None

def email_exists(cursor, email):
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    return cursor.fetchone() is not None

# signup function, takes in user details from frontend and returns success status and message
def signup_user(name, username, email, confirm_email, password):
    if email != confirm_email:
        return False, "Emails do not match"

    verification_code = generate_verification_code()
    hashed_password = hash_password(password)

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        if username_exists(cursor, username):
            return False, "Username already in use"

        if email_exists(cursor, email):
            return False, "Email already in use"

        insert_query = """
        INSERT INTO users 
        (name, username, email, password_hash, email_verified, email_verification_code)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (name, username, email, hashed_password, False, verification_code)
        )
        connection.commit()

        try:
            send_verification_email(email, verification_code)
        except Exception:
            return False, "Email address does not exist or cannot receive mail"

        return True, "Signup successful. Verification code sent."

    except mysql.connector.IntegrityError:
        # Safety net (should not usually hit now)
        return False, "Username or email already in use"

    except mysql.connector.Error:
        return False, "Internal database error"

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()