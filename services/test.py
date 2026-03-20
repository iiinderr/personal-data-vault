from auth import create_access_token, decode_access_token

token = create_access_token(
    user_id=1,
    username="inder",
    role="admin"
)

print("Token:", token)

payload = decode_access_token(token)

print("Decoded payload:", payload)