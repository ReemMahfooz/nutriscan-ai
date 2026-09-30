from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


password = "TestPassword123"

hashed = hash_password(password)

print("Original password:")
print(password)

print("\nHashed password:")
print(hashed)

print("\nCorrect password verification:")
print(verify_password(password, hashed))

print("\nWrong password verification:")
print(verify_password("WrongPassword", hashed))


token = create_access_token(123)

print("\nJWT:")
print(token)

user_id = decode_access_token(token)

print("\nUser ID from JWT:")
print(user_id)