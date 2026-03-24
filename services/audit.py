# ── Imports ─────────────────────────────────────────

from datetime import datetime
from models.database import AuditLog, SessionLocal


# ── Audit Logger Class ──────────────────────────────

class AuditLogger:
    """
    Responsible for writing audit logs to the database.

    Key idea:
    - Every important action is recorded
    - Logs are write-only (never updated or deleted)
    """

    def log(
        self,
        action: str,
        user_id: int | None = None,
        resource_type: str | None = None,
        resource_id: int | None = None,
        details: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """
        Creates and stores an audit log entry.
        """

        db = SessionLocal()  # Create DB session

        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                timestamp=datetime.utcnow(),
            )

            db.add(entry)     # Add log
            db.commit()       # Save to DB

        except Exception as e:
            db.rollback()     # Undo if error
            print(f"[AUDIT ERROR]: {e}")

        finally:
            db.close()        # Always close session

    def get_logs_for_user(self, user_id: int, limit: int = 100) -> list:
        """
        Fetch recent audit logs for a specific user.
    
        - Returns latest logs first
        - Uses limit to avoid loading too much data
        """
    
        db = SessionLocal()
    
        try:
            logs = (
                db.query(AuditLog)
                  .filter(AuditLog.user_id == user_id)   # filter by user
                  .order_by(AuditLog.timestamp.desc())   # latest first
                  .limit(limit)                          # restrict results
                  .all()
            )
    
            return logs
    
        finally:
            db.close()     
    
    def get_all_logs(self, limit: int = 500) -> list:
        """
        Fetch recent audit logs for all users.
    
        - Intended for admin use only
        - Returns latest logs first
        """
    
        db = SessionLocal()
    
        try:
            logs = (
                db.query(AuditLog)
                  .order_by(AuditLog.timestamp.desc())  # newest first
                  .limit(limit)                         # restrict results
                  .all()
            )
    
            return logs
    
        finally:
            db.close()

# ── Audit Action Constants ─────────────────────────

class AuditAction:
    """
    Centralized list of all audit actions.

    Why?
    - Prevent typos in string values
    - Easy to manage and search actions
    """

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED  = "LOGIN_FAILED"
    LOGOUT        = "LOGOUT"

    CREATE_NOTE   = "CREATE_NOTE"
    READ_NOTE     = "READ_NOTE"
    UPDATE_NOTE   = "UPDATE_NOTE"
    DELETE_NOTE   = "DELETE_NOTE"

    CREATE_USER   = "CREATE_USER"
    DELETE_USER   = "DELETE_USER"

    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"

    CREATE_DOCUMENT = "CREATE_DOCUMENT"

    CREATE_HINT = "CREATE_HINT"

    READ_HINT = "READ_HINT"

    UPDATE_USER_ROLE = "UPDATE_USER_ROLE"

#added this line
audit_logger = AuditLogger()