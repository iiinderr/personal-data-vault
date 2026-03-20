# test_schema.py

from routes.users import RegisterRequest

# Valid case
user = RegisterRequest(
    username="inder",
    email="inder@test.com",
    password="12345678"
)
print(user)

# Invalid password
user = RegisterRequest(
    username="inder",
    email="inder@test.com",
    password="123"
)