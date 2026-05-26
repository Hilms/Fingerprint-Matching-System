from fastapi import APIRouter, Depends, HTTPException

from app.security.auth import get_current_user
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_service = UserService()

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


@router.put("/{username}")
async def update_user(
    username: str,
    current_user = Depends(get_current_user)
):
    return await user_service.update_user(username)