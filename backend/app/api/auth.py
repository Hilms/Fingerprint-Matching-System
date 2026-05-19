from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.security.auth import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

fake_users = {}

class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(data: RegisterRequest):

    # check if user exist
    if data.username in fake_users:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # store user
    fake_users[data.username] = {

        "username": data.username,

        # store hashed pw
        "password": hash_password(data.password)
    }

    return {
        "message": "User created"
    }