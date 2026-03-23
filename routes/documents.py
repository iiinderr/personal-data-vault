
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

from models.database import SessionLocal, DocumentMetadata
from routes.users import get_current_user
from services.encryption import get_encryption_service
from services.audit import audit_logger, AuditAction

router = APIRouter()


class DocumentCreateRequest(BaseModel):
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    file_path: str
    tags: Optional[str] = None


@router.post("/", status_code=201)
def create_document(
    body: DocumentCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()
    user_id = int(current_user["sub"])

    try:
        enc = get_encryption_service()

        # Encrypt sensitive file path before saving
        encrypted_path = enc.encrypt(body.file_path)

        doc = DocumentMetadata(
            file_name=body.file_name,
            file_type=body.file_type,
            file_size=body.file_size,
            encrypted_file_path=encrypted_path,
            tags=body.tags,
            user_id=user_id,
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Audit logging (important for production systems)
        audit_logger.log(
            action=AuditAction.CREATE_DOCUMENT,
            user_id=user_id,
            resource_type="document_metadata",
            resource_id=doc.id,
            details=f"Stored metadata for '{body.file_name}'",
            ip_address=request.client.host,
        )

        return {
            "message": "Document metadata saved",
            "document_id": doc.id
        }

    finally:
        db.close()

@router.get("/")
def list_documents(current_user: dict = Depends(get_current_user)):
    """
    Lists all document metadata for the current user.
    Admin can see all documents.
    """
    db = SessionLocal()
    user_id = int(current_user["sub"])
    role = current_user.get("role", "viewer")

    try:
        query = db.query(DocumentMetadata)

        # If not admin, only show user's documents
        if role != "admin":
            query = query.filter(DocumentMetadata.user_id == user_id)

        docs = query.all()

        return [
            {
                "id": d.id,
                "file_name": d.file_name,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "tags": d.tags,
                "user_id": d.user_id,
                # NOTE: encrypted_file_path is NOT returned (security)
            }
            for d in docs
        ]

    finally:
        db.close()

