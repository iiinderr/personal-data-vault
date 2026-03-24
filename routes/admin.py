
from fastapi import APIRouter, Depends, HTTPException
from routes.users import get_current_user
from models.database import SessionLocal, User, UserRole
from services.audit import audit_logger, AuditAction

router = APIRouter()

def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency that blocks non-admins from accessing admin routes.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    
    return current_user

@router.get("/audit-logs")
def get_audit_logs(current_user: dict = Depends(require_admin)):
    """
    Returns recent audit logs.
    Only accessible by admins.
    """
    logs = audit_logger.get_all_logs(limit=500)

    return [
        {
            "id":            log.id,
            "user_id":       log.user_id,
            "action":        log.action,
            "resource_type": log.resource_type,
            "resource_id":   log.resource_id,
            "details":       log.details,
            "ip_address":    log.ip_address,
            "timestamp":     log.timestamp.isoformat(),
        }
        for log in logs
    ]

@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: str,
    current_user: dict = Depends(require_admin)
):
    """
    Changes a user's role. Admin only.
    Valid values: "admin", "editor", "viewer"
    """

    valid_roles = [r.value for r in UserRole]

    # Validate role first
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Choose from: {valid_roles}"
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        old_role = user.role.value
        user.role = UserRole(new_role)

        db.commit()

        # Audit log 
        audit_logger.log(
            action        = AuditAction.UPDATE_USER_ROLE,
            user_id       = int(current_user["sub"]),
            resource_type = "users",
            resource_id   = user_id,
            details       = f"Changed user '{user.username}' role from '{old_role}' to '{new_role}'.",
        )

        return {
            "message": f"User '{user.username}' role updated to '{new_role}'."
        }

    finally:
        db.close()