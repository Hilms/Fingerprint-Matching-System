from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.dependencies import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.post("/data")
async def get_dashboard_data(
    user=Depends(get_current_user)
 ):
    return await dashboard_service.get_dashboard_data()

@router.post("/admin/data")
async def get_dashboard_admin_data(
    user=Depends(get_current_user),
    _=Depends(require_role('admin'))
 ):
    return await dashboard_service.get_dashboard_admin_data()