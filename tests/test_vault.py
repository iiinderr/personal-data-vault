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

class TestRBAC:

    def test_require_role_admin_blocks_viewer(self):
        
        from services.auth import require_role

        @require_role("admin")
        def admin_only(current_user):
            return "secret"

        viewer = {"sub": "1", "role": "viewer"}

        with pytest.raises(PermissionError):
            admin_only(viewer)

    def test_require_role_admin_allows_admin(self):
        
        from services.auth import require_role

        @require_role("admin")
        def admin_only(current_user):
            return "secret"

        admin = {"sub": "1", "role": "admin"}

        assert admin_only(admin) == "secret"

    def test_is_owner_allows_owner(self):
        
        from services.auth import is_owner_or_admin

        user = {"sub": "5", "role": "editor"}

        assert is_owner_or_admin(user, resource_owner_id=5) is True

    def test_is_owner_blocks_other_user(self):
        
        from services.auth import is_owner_or_admin

        user = {"sub": "3", "role": "editor"}

        assert is_owner_or_admin(user, resource_owner_id=5) is False

    def test_admin_can_access_any_resource(self):
        
        from services.auth import is_owner_or_admin

        admin = {"sub": "1", "role": "admin"}

        assert is_owner_or_admin(admin, resource_owner_id=999) is True