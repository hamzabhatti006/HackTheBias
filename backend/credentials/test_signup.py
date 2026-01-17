from signup import signup_user

print("=== TEST SIGNUP ===")

name = input("Name: ")
username = input("Username: ")
email = input("Email: ")
confirm_email = input("Confirm Email: ")
password = input("Password: ")

success, message = signup_user(
    name=name,
    username=username,
    email=email,
    confirm_email=confirm_email,
    password=password
)

print("\nRESULT:")
print("Success:", success)
print("Message:", message)