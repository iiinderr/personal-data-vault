
from fastapi import APIRouter, Depends, HTTPException
from routes.users import get_current_user

router = APIRouter()


def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency that blocks non-admins from accessing admin routes.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    
    return current_user