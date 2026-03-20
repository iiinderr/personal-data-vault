# ── Imports ─────────────────────────────
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, field_validator

from models.database import SessionLocal, User
from services.auth import verify_password, create_access_token
from services.audit import audit_logger, AuditAction


# ── Router ─────────────────────────────
router = APIRouter()


# ── Schemas ────────────────────────────

# ✅ Step 1 (your existing code stays here)
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


# ✅ Step 2 (new schema)
class LoginRequest(BaseModel):
    username: str
    password: str


# ── Routes ─────────────────────────────

@router.post("/login")
def login(body: LoginRequest, request: Request):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == body.username).first()

        if not user or not verify_password(body.password, user.password_hash):
            audit_logger.log(
                action=AuditAction.LOGIN_FAILED,
                details=f"Failed login for username '{body.username}'",
                ip_address=request.client.host,
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role.value
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }

    finally:
        db.close()