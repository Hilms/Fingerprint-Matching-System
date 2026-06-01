from fastapi import HTTPException, Depends

from app.security.auth import get_current_user

def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)):

        if user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )

        return user

    return checker