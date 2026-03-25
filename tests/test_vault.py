import os
import pytest

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

        # Tamper with ciphertext
        tampered = ciphertext[:-5] + "abcde"

        with pytest.raises(ValueError):
            self.enc.decrypt(tampered)