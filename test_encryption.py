from services.encryption import generate_key, EncryptionService

key = generate_key()

service = EncryptionService(key)

text = "my secret note"

# encrypt
encrypted = service.encrypt(text)
print("Encrypted:", encrypted)

# decrypt
decrypted = service.decrypt(encrypted)
print("Decrypted:", decrypted)