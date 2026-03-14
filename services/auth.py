# ── Imports ─────────────────────────────────────────
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# JWT secret key used to sign tokens
JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_THIS_IN_PRODUCTION")

# algorithm used for signing
JWT_ALGORITHM = "HS256"

# token expiry time
TOKEN_EXPIRY_MINUTES = 60


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

def create_access_token(user_id: int, username: str, role: str) -> str:
    """
    Create a JWT token for authenticated users.

    The token contains user information and expiry time.
    """

    # get current time in UTC
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),                              # subject (user id)
        "username": username,
        "role": role,
        "exp": now + timedelta(minutes=TOKEN_EXPIRY_MINUTES),  # expiry time
        "iat": now                                        # issued at
    }

    # sign the token using our secret key
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token

def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    The function verifies:
    - the signature (token was not tampered with)
    - the expiry time
    - the algorithm used

    Returns the decoded payload if valid.
    """

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except ExpiredSignatureError:
        # Token was valid but expired
        raise ValueError("[AUTH] Token has expired. Please log in again.")

    except InvalidTokenError as e:
        # Covers tampered tokens, malformed tokens, wrong signature, etc.
        raise ValueError(f"[AUTH] Invalid token: {str(e)}")