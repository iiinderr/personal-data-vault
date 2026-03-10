# ── Imports ──────────────────────────────────────────────
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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
    
    def encrypt_field(self, value: str | None) -> str | None:
        """
        Helper method to safely encrypt optional fields.

        Some database columns may contain NULL values.
        If we try to encrypt None, the program would crash.

        This function checks if the value exists before encrypting.
        """

        if value is None:
            return None

        return self.encrypt(value)


    def decrypt_field(self, value: str | None) -> str | None:
        """
        Helper method to safely decrypt optional fields.

        If the value is None (NULL in database),
        we simply return None instead of decrypting.
        """

        if value is None:
            return None

        return self.decrypt(value)
    
def derive_key_from_password(password: str, salt: bytes = None):
    """
    Derives a secure Fernet encryption key from a user password.

    Why we do this:
    Instead of storing encryption keys directly, we can generate
    them from user passwords using a Key Derivation Function.

    PBKDF2 applies hashing many times to make brute-force attacks slower.

    Returns:
        (fernet_key, salt)
    """

    # If no salt is provided, generate a new random one
    if salt is None:
        salt = os.urandom(16)

    # Configure PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),   # hashing algorithm
        length=32,                   # output key length
        salt=salt,                   # random salt
        iterations=390000,           # recommended iteration count
    )

    # derive raw key bytes from password
    key_bytes = kdf.derive(password.encode())

    # Fernet requires base64 encoded key
    fernet_key = base64.urlsafe_b64encode(key_bytes)

    return fernet_key, salt