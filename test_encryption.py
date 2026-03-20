from services.encryption import derive_key_from_password, EncryptionService

password = "vault_password"

key, salt = derive_key_from_password(password) 

service = EncryptionService(key)

text = "secret vault note"

encrypted = service.encrypt_field(text)
print("Encrypted:", encrypted)

decrypted = service.decrypt_field(encrypted)
print("Decrypted:", decrypted)

# test None case
print("None encryption:", service.encrypt_field(None))
print("None decryption:", service.decrypt_field(None))
