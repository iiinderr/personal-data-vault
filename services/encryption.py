import os
from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def load_key_from_env(env_var="VAULT_ENCRYPTION_KEY"):
    key = os.environ.get(env_var)

    if not key:
        raise ValueError("Encryption key not set")

    return key.encode()