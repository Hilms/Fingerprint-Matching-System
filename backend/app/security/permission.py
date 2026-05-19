from fastapi import HTTPException

def require_role(required_role: str):
    def checker(user: dict):

        if user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )

        return user

    return checker