from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.security.auth import hash_password, verify_password, create_access_token, get_current_user
from app.security.permission import require_role

from app.dependencies import user_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(data: RegisterRequest):

    existing = await user_service.get_user(
            data.username
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="user already exists"
        )

    await user_service.create_user(data)

    return {
        "message": "user created"
    }


@router.post("/login")
async def login(data: LoginRequest):

    user = await user_service.get_user_with_password(
        data.username
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="wrong username"
        )

    if not user["is_active"]:

        raise HTTPException(
            status_code=403,
            detail="user deactivated"
        )

    valid_password = verify_password(
        data.password,
        user["password_hash"]
    )

    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="wrong password"
        )

    token = create_access_token({
        "sub": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def me(
    user=Depends(get_current_user)
):
    return user