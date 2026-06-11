from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
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


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register")
async def register(data: RegisterRequest):

    existing_user = await user_service.get_user(
            data.username
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="user already exists"
        )

    existing_mail = await user_service.get_user_mail(
        data.email
    )

    if existing_mail:
        raise HTTPException(
           status_code=409,
           detail="email already exists"
        )

    await user_service.create_user(data)

    return {
        "message": "user successfully created"
    }


@router.post("/login")
async def login(data: LoginRequest):

    user = await user_service.get_user_with_password(
        data.username
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
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
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "type": 'access'
    })

    refresh_token = create_refresh_token({
        "sub": user["username"],
        "role": user["role"],
        "type": 'refresh'
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():
    return {
        "message": "logout successful"
    }

@router.get("/me")
async def me(
    user=Depends(get_current_user)
):
    return user

@router.post("/refresh")
async def refresh(data: RefreshRequest):

    try:
        payload = decode_token(data.refresh_token)
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # IMPORTANT: ensure it's actually a refresh token
    if payload["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload["role"],
        "type": 'access'
    })

    return {
        "access_token": new_access_token
    }