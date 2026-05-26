from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.services.subject_service import SubjectService
from app.services.storage_service import StorageService


router = APIRouter(
    prefix="/subjects",
    tags=["subjects"]
)

subject_service = SubjectService()
storage_service = StorageService()

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
def create_subject(
    data: SubjectCreate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return subject_service.create_subject(data.dict())

@router.get("/{subject_id}")
def get_subject(
    subject_id: int,
    user=Depends(get_current_user)
):
    return subject_service.get_subject(subject_id)

@router.get("/search/")
def search_subjects(
    q: str,
    user=Depends(get_current_user)
):
    return subject_service.search_subjects(q)

@router.put("/{subject_id}")
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return subject_service.update_subject(
        subject_id,
        data.dict()
    )

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return subject_service.delete_subject(subject_id)