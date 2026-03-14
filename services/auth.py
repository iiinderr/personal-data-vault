"""
auth.py — Authentication utilities.

Currently handles:
1. Password hashing using bcrypt
"""

# ── Imports ─────────────────────────────────────────

import bcrypt   # Library used for secure password hashing


# ── Password Utilities ──────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    bcrypt automatically generates a random salt and
    stores it inside the hash itself.

    Returns a hashed password string that can be safely
    stored in the database.
    """

    # bcrypt works with bytes, so convert the string password to bytes
    password_bytes = plain_password.encode("utf-8")

    # generate a salt with work factor 12
    salt = bcrypt.gensalt(rounds=12)

    # hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)

    # convert bytes back to string for storage
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plain password with a stored bcrypt hash.
    """

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )