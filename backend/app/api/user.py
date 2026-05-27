from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role
from app.dependencies import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class SelfUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class AdminPasswordReset(BaseModel):
    new_password: str

@router.get("/search")
async def search_user(
    query: str,
    current_user = Depends(get_current_user)
):
    return await user_service.search_user(query)

@router.get("/{username}")
async def get_user(
    username: str,
    current_user = Depends(get_current_user)
):
    user = user_service.get_user(username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return await user

@router.delete("/{username}")
async def delete_user(
    username: str,
    current_user = Depends(get_current_user)
):
    return await user_service.delete_user(username)


@router.patch("/{username}")
async def admin_update_user(
    username: str,
    data: AdminUserUpdate,
    current_user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    return await user_service.update_user(
        username=username,
        data=data.dict()
    )

@router.patch("/me")
async def update_me(
    data: SelfUserUpdate,
    current_user=Depends(get_current_user)
):

    return await user_service.update_user(
        username=current_user["username"],
        data=data.dict()
    )

@router.patch("/me/password")
async def update_password(
    data: PasswordUpdate,
    current_user=Depends(get_current_user)
):

    return await user_service.update_password(
        username=current_user["username"],
        current_password=data.current_password,
        new_password=data.new_password
    )

@router.patch("/{username}/password")
async def admin_reset_password(
    username: str,
    data: AdminPasswordReset,
    current_user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    return await user_service.admin_reset_password(
        username=username,
        new_password=data.new_password
    )