from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.dependencies import subject_service

router = APIRouter(
    prefix="/subjects",
    tags=["subjects"]
)

class SubjectCreate(BaseModel):
    external_id: int
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    phone_number: str | None = None

class SubjectUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    phone_number: str | None = None

# PUBLIC ROUTES

@router.get("/all")
async def get_subjects(
    user=Depends(get_current_user)
):
    return await subject_service.get_subjects()

@router.get("/search")
async def search_subjects(
    q: str,
    user=Depends(get_current_user)
):
    return await subject_service.search_subjects(q)

@router.get("/id/{external_id}")
async def get_subject(
    external_id: int,
    user=Depends(get_current_user)
):
    return await subject_service.get_subject(external_id)


# ADMIN ROUTES
@router.post("/admin/create")
async def create_subject(
    data: SubjectCreate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.create_subject(
        data.model_dump()
    )

@router.patch("/admin/update/id/{external_id}")
async def update_subject(
    external_id: int,
    data: SubjectUpdate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.update_subject(
        external_id,
        data.model_dump(exclude_none=True)
    )

@router.delete("/admin/delete/id/{external_id}")
async def delete_subject(
    external_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.delete_subject(
        external_id
    )