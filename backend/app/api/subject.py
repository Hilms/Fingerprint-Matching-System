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
    ref_id: str
    name: str
    age: int
    address: str
    city: str
    country: str


class SubjectUpdate(BaseModel):
    name: str
    age: int
    address: str
    city: str
    country: str


@router.post("/")
async def create_subject(
    data: SubjectCreate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.create_subject(data.dict())


@router.get("/search/")
async def search_subjects(
    q: str,
    user=Depends(get_current_user)
):
    return await subject_service.search_subjects(q)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: int,
    user=Depends(get_current_user)
):
    return await subject_service.get_subject(subject_id)


@router.put("/{subject_id}")
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.update_subject(
        subject_id,
        data.dict()
    )


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await subject_service.delete_subject(subject_id)