# ── Imports ─────────────────────────────
from fastapi import APIRouter, HTTPException, Request, Depends, Header 
from pydantic import BaseModel, EmailStr, field_validator

from models.database import SessionLocal, User ,UserRole
from services.auth import verify_password, create_access_token ,decode_access_token , hash_password
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

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.split(" ")[1]

    try:
        payload = decode_access_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    

@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    db = SessionLocal()

    try:
        user_id = int(current_user["sub"])
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active
        }

    finally:
        db.close()

@router.post("/register", status_code=201)
def register_user(body: RegisterRequest, request: Request):
    db = SessionLocal()

    try:
        # Check if user already exists
        existing = db.query(User).filter(
            (User.username == body.username) | (User.email == body.email)
        ).first()

        if existing:
            raise HTTPException(status_code=409, detail="Username or email already exists")

        # Hash password
        hashed_password = hash_password(body.password)

        # Create user
        new_user = User(
            username=body.username,
            email=body.email,
            password_hash=hashed_password,
            role=UserRole.VIEWER
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }

    finally:
        db.close()
