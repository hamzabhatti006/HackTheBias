# will connect frontend to backend trust

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)  # allow frontend to call backend

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "strain3872AK",
    "database": "silent_speak_db",
    "port": 3306
}

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

# ---------- HELPER FUNCTIONS ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))

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

def username_exists(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    return cursor.fetchone() is not None

def email_exists(cursor, email):
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    return cursor.fetchone() is not None

def login_user(username: str, password: str):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT password_hash, email_verified
            FROM users
            WHERE username = %s
        """, (username,))
        result = cursor.fetchone()

        # app.logger.info(f"DB result: {result}")

        if not result:
            app.logger.info("User not found in database")
            return {"login": False, "message": "User does not exist"}

        stored_hash, email_verified = result

        # app.logger.info(f"stored_hash type: {type(stored_hash)}")
        # app.logger.info(f"stored_hash repr: {repr(stored_hash)}")
        # app.logger.info(f"stored_hash length: {len(stored_hash) if stored_hash else 0}")
        # app.logger.info(f"email_verified: {email_verified}")

        if not email_verified:
            app.logger.info("Email not verified")
            return {"login": False, "message": "Email not verified"}

        # Handle different hash storage formats
        if isinstance(stored_hash, str):
            stored_hash_bytes = stored_hash.encode("utf-8")
        else:
            stored_hash_bytes = stored_hash

        password_bytes = password.encode("utf-8")

        # app.logger.info(f"Checking password with bcrypt...")
        # app.logger.info(f"Password to check: {password}")
        # app.logger.info(f"Hash starts with: {stored_hash[:10] if stored_hash else 'None'}")

        if not bcrypt.checkpw(password_bytes, stored_hash_bytes):
            # app.logger.info("Password check FAILED")
            return {"login": False, "message": "Incorrect password"}

        # app.logger.info("Password check PASSED")
        return {"login": True, "message": "Login successful"}

    except mysql.connector.Error as e:
        # app.logger.exception(f"DB error: {e}")
        return {"login": False, "message": "Internal server error"}
    except Exception as e:
        # app.logger.exception(f"Unexpected error: {e}")
        return {"login": False, "message": "Internal server error"}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.post("/login")
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    # app.logger.info(f"Login attempt for username: {username}")

    if not username or not password:
        return jsonify({"login": False, "message": "Missing fields"}), 400

    # TEMP: Generate a test hash to compare format
    test_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # app.logger.info(f"Test hash format: {test_hash}")
    # app.logger.info(f"Test hash decoded: {test_hash.decode('utf-8')}")

    result = login_user(username, password)

    if result["login"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.post("/signup")
def signup():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email0 = data.get("email0", "").strip()
    email1 = data.get("email1", "").strip()
    name = data.get("name", "").strip()  # ✅ Add this
    
    app.logger.info(f"Signup attempt for username: {username}")
    
    # Validate input
    if not username or not password or not email0 or not email1 or not name:  # ✅ Add name check
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    # Check if emails match
    if email0 != email1:
        return jsonify({"success": False, "message": "Emails do not match"}), 400
    
    # Validate email format (basic check)
    if "@" not in email0 or "." not in email0:
        return jsonify({"success": False, "message": "Invalid email format"}), 400
    
    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Username already exists"}), 409
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email0,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already registered"}), 409
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        app.logger.info(f"Generated hash for {username}: {password_hash}")
        
        # Insert new user with name ✅ UPDATED
        cursor.execute("""
            INSERT INTO users (username, name, email, password_hash, email_verified)
            VALUES (%s, %s, %s, %s, 0)
        """, (username, name, email0, password_hash))
        
        connection.commit()
        
        app.logger.info(f"User {username} created successfully")
        
        return jsonify({
            "success": True,
            "message": "Account created successfully! Please verify your email."
        }), 201
        
    except mysql.connector.Error as e:
        app.logger.exception(f"DB error during signup: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    except Exception as e:
        app.logger.exception(f"Unexpected error during signup: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
if __name__ == "__main__":
    app.run(debug=True, port=5000)