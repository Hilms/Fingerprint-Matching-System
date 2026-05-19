from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.security.auth import hash_password, verify_password, create_access_token, get_current_user
from app.security.permission import require_role

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
        "password": hash_password(data.password),

        "role": "user"
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

    # create jwt token
    token = create_access_token({
        "sub": data.username,
        "role": data.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def me(user = Depends(get_current_user)):
    return user

@router.post("/upload")
def upload(
    user = Depends(get_current_user),
    _ = Depends(require_role("admin"))
):
    return {"message": "admin upload ok"}