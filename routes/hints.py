
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional

from models.database import SessionLocal, PasswordHint
from routes.users import get_current_user
from services.encryption import get_encryption_service
from services.audit import audit_logger, AuditAction

router = APIRouter()


class HintCreateRequest(BaseModel):
    service_name: str
    hint: str
    url: Optional[str] = None


@router.post("/", status_code=201)
def create_hint(
    body: HintCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    user_id = int(current_user["sub"])

    try:
        enc = get_encryption_service()

        # Encrypt hint before storing (security)
        encrypted_hint = enc.encrypt(body.hint)

        hint = PasswordHint(
            service_name=body.service_name,
            encrypted_hint=encrypted_hint,
            url=body.url,
            user_id=user_id,
        )

        db.add(hint)
        db.commit()
        db.refresh(hint)

        # Audit log
        audit_logger.log(
            action=AuditAction.CREATE_HINT,
            user_id=user_id,
            resource_type="password_hints",
            resource_id=hint.id,
            details=f"Created hint for {body.service_name}",
            ip_address=request.client.host,
        )

        return {"message": "Hint saved", "hint_id": hint.id}

    finally:
        db.close()