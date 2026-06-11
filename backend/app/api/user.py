from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import user_service
from app.security.auth import get_current_user
from app.security.permission import require_role

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class newUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class SelfUserUpdate(BaseModel):
    # username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class AdminUserUpdate(BaseModel):
    # username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class AdminPasswordReset(BaseModel):
    new_password: str


# SELF
@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user)
):
    return await user_service.get_user(
        current_user["username"]
    )


@router.patch("/me")
async def update_me(
    data: SelfUserUpdate,
    current_user=Depends(get_current_user)
):
    return await user_service.update_user(
        current_user["username"],
        data.model_dump(exclude_none=True)
    )


@router.patch("/me/password")
async def update_my_password(
    data: PasswordUpdate,
    current_user=Depends(get_current_user)
):
    return await user_service.update_password(
        current_user["username"],
        data.current_password,
        data.new_password
    )


@router.delete("/me")
async def delete_me(
    current_user=Depends(get_current_user)
):
    return await user_service.delete_user(
        current_user["username"]
    )


# ADMIN
@router.get("/admin")
async def get_all_users(
    _=Depends(require_role("admin"))
):
    return await user_service.get_all_users()


@router.post("/admin/create")
async def create_user(
    data: newUser,
    _=Depends(require_role("admin"))
):
    return await user_service.create_user(data)


@router.get("/admin/search")
async def search_users(
    query: str,
    _=Depends(require_role("admin"))
):
    return await user_service.search_users(query)


@router.get("/admin/{username}")
async def get_user(
    username: str,
    _=Depends(require_role("admin"))
):
    return await user_service.get_user(
        username
    )


@router.patch("/admin/{username}")
async def admin_update_user(
    username: str,
    data: AdminUserUpdate,
    _=Depends(require_role("admin"))
):
    return await user_service.update_user(
        username,
        data.model_dump(exclude_none=True)
    )


@router.patch("/admin/{username}/password")
async def admin_reset_password(
    username: str,
    data: AdminPasswordReset,
    _=Depends(require_role("admin"))
):
    return await user_service.admin_reset_password(
        username,
        data.new_password
    )


@router.delete("/admin/{username}")
async def admin_delete_user(
    username: str,
    _=Depends(require_role("admin"))
):
    return await user_service.delete_user(
        username
    )