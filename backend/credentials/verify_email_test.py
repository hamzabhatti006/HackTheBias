from verify_email import verify_email

payload = {
    "code": "494848"
}

response = verify_email(payload)
print(response)