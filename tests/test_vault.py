import os
import pytest
from cryptography.fernet import InvalidToken

os.environ["VAULT_ENCRYPTION_KEY"] = "test-password-123"


class TestEncryption:

    def setup_method(self):
        
        from services.encryption import EncryptionService, derive_key_from_password

        key, self.salt = derive_key_from_password("test-password-123")
        self.enc = EncryptionService(key)

    def test_encrypt_decrypt(self):
        
        plaintext = "my secret note"

        ciphertext = self.enc.encrypt(plaintext)
        recovered  = self.enc.decrypt(ciphertext)

        assert recovered == plaintext

    def test_tampered_ciphertext_raises(self):
        ciphertext = self.enc.encrypt("sensitive data")

        tampered = ciphertext[:-5] + "abcde"

        with pytest.raises(InvalidToken):
            self.enc.decrypt(tampered)

class TestAuth:

    def test_hash_password_not_equal_to_plain(self):
        
        from services.auth import hash_password

        password = "mypassword"
        hashed = hash_password(password)

        assert hashed != password

    def test_verify_password_correct(self):
        
        from services.auth import hash_password, verify_password

        password = "correcthorse"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_wrong(self):
        
        from services.auth import hash_password, verify_password

        hashed = hash_password("correcthorse")

        assert verify_password("wrongpassword", hashed) is False

    def test_jwt(self):
        
        from services.auth import create_access_token, decode_access_token

        token = create_access_token(user_id=42, username="alice", role="editor")

        payload = decode_access_token(token)

        assert payload["sub"] == "42"
        assert payload["username"] == "alice"
        assert payload["role"] == "editor"

    def test_invalid_jwt_raises(self):
    
        from services.auth import decode_access_token

        with pytest.raises(ValueError):
            decode_access_token("this.is.not.valid")