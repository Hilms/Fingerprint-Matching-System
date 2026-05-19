from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.security.auth import hash_password
from app.security.auth import verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

fake_users = {}

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
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

@router.post("/login")
def login(data: LoginRequest):

    user = fake_users.get(data.username)

    if not user:
        return {
            "error": "wrong username"
        }

    if not verify_password(data.password, user["password"]):
        return {
            "error": "wrong password"
        }

    return {
        "message": "login successful"
    }