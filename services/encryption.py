# ── Imports ──────────────────────────────────────────────
import os
from cryptography.fernet import Fernet


# ── Key utilities ─────────────────────────────────────────

def generate_key() -> bytes:
    """
    Generates a random Fernet encryption key.

    This key should be generated once and stored
    securely in an environment variable.
    """
    return Fernet.generate_key()


def load_key_from_env(env_var: str = "VAULT_ENCRYPTION_KEY") -> bytes:
    """
    Loads the encryption key from an environment variable.

    Using environment variables prevents secrets
    from being hardcoded in the source code.
    """

    key = os.environ.get(env_var)

    if not key:
        raise ValueError(
            f"Encryption key '{env_var}' is not set in environment variables."
        )

    return key.encode()


# ── Encryption Service ────────────────────────────────────

class EncryptionService:
    """
    Wrapper class around Fernet encryption.

    This service provides a clean interface for
    encrypting sensitive data before storing it
    in the database.
    """

    def __init__(self, key: bytes):
        """
        Initialize Fernet with the provided key.
        """

        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts a plaintext string.

        Process:
        string -> bytes -> encrypted -> string
        """

        # Fernet expects bytes, so we convert string to bytes
        plaintext_bytes = plaintext.encode("utf-8")

        # Encrypt the data
        encrypted_bytes = self._fernet.encrypt(plaintext_bytes)

        # Convert encrypted bytes back to string for storage
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypts encrypted data back to plaintext.

        Steps:
        1. Convert ciphertext string to bytes
        2. Use Fernet to decrypt it
        3. Convert decrypted bytes back to string
        """

        # Fernet expects bytes input
        ciphertext_bytes = ciphertext.encode("utf-8")

        # Decrypt the ciphertext
        decrypted_bytes = self._fernet.decrypt(ciphertext_bytes)

        # Convert decrypted bytes back to string
        return decrypted_bytes.decode("utf-8")