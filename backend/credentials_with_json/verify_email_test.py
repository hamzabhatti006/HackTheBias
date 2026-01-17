from verify_email import verify_email

payload = {
    "code": "800524"
}

response = verify_email(payload)
print(response)