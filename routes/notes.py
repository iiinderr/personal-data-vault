from fastapi import APIRouter, Depends, Request , HTTPException
from pydantic import BaseModel
from typing import Optional

from models.database import SessionLocal, EncryptedNote
from routes.users import get_current_user
from services.encryption import get_encryption_service
from services.audit import audit_logger, AuditAction
from services.auth import is_owner_or_admin


router = APIRouter()

class NoteCreateRequest(BaseModel):
    title: str
    content: str
    encryption_key_hint: Optional[str] = None


@router.post("/", status_code=201)
def create_note(
    body: NoteCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    enc = get_encryption_service()
    db = SessionLocal()

    try:
        encrypted_content = enc.encrypt(body.content)

        user_id = int(current_user["sub"])

        note = EncryptedNote(
            title=body.title,
            encrypted_content=encrypted_content,
            encryption_key_hint=body.encryption_key_hint,
            user_id=user_id,
        )

        db.add(note)
        db.commit()
        db.refresh(note)

        audit_logger.log(
            action=AuditAction.CREATE_NOTE,
            user_id=user_id,
            resource_type="encrypted_notes",
            resource_id=note.id,
            details=f"Created note '{body.title}'.",
            ip_address=request.client.host,
        )

        return {"message": "Note created.", "note_id": note.id}

    finally:
        db.close()

@router.get("/")
def list_notes(current_user: dict = Depends(get_current_user)):
    """
    Returns all notes for the logged-in user.
    Admin can see all notes, normal users see only their own.
    """
    db = SessionLocal()

    user_id = int(current_user["sub"])
    role = current_user.get("role", "viewer")

    try:
        query = db.query(EncryptedNote)

        # If not admin → only own notes
        if role != "admin":
            query = query.filter(EncryptedNote.user_id == user_id)

        notes = query.all()

        # Return only metadata (NOT decrypted content)
        return [
            {
                "id": n.id,
                "title": n.title,
                "encryption_key_hint": n.encryption_key_hint,
                "user_id": n.user_id,
                "created_at": n.created_at.isoformat(),
            }
            for n in notes
        ]

    finally:
        db.close()

@router.get("/{note_id}")
def get_note(
    note_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch a single note and decrypt its content.
    """
    enc = get_encryption_service()
    db = SessionLocal()

    try:
        note = db.query(EncryptedNote).filter(EncryptedNote.id == note_id).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Ownership / admin check
        if not is_owner_or_admin(current_user, note.user_id):
            audit_logger.log(
                action=AuditAction.UNAUTHORIZED_ACCESS,
                user_id=int(current_user["sub"]),
                resource_type="encrypted_notes",
                resource_id=note_id,
                ip_address=request.client.host,
            )
            raise HTTPException(status_code=403, detail="Access denied")

        # Decrypt content
        decrypted_content = enc.decrypt(note.encrypted_content)

        audit_logger.log(
            action=AuditAction.READ_NOTE,
            user_id=int(current_user["sub"]),
            resource_type="encrypted_notes",
            resource_id=note_id,
            ip_address=request.client.host,
        )

        return {
            "id": note.id,
            "title": note.title,
            "content": decrypted_content,
            "encryption_key_hint": note.encryption_key_hint,
            "user_id": note.user_id,
        }

    finally:
        db.close()