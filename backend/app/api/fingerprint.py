from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.dependencies import fingerprint_service

router = APIRouter(
    prefix="/fingerprints",
    tags=["fingerprints"]
)

ALLOWED_TYPES = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/bmp"]

class FingerprintCreate(BaseModel):
    subject_id: int
    sex: str
    hand: str
    finger: str
    filename: str


# UPLOAD (ADMIN)
@router.post("/upload")
async def upload_fingerprint(
    subject_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    if file.content_type not in ALLOWED_TYPES:

        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    return await fingerprint_service.upload_fingerprint(
        file,
        subject_id,
        user
    )


# CREATE FINGERPRINT (MANUAL / IMPORT USE CASE / ADMIN)
@router.post("/")
async def create_fingerprint(
    data: FingerprintCreate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await fingerprint_service.create_fingerprint(
        data.dict()
    )


# SEARCH (USER + ADMIN)
@router.get("/search")
async def search_fingerprints(
    q: str,
    user=Depends(get_current_user)
):
    return await fingerprint_service.search_fingerprints(q)


# METADATA
@router.get("/{fingerprint_id}")
async def get_metadata(
    fingerprint_id: int,
    user=Depends(get_current_user)
):
    return await fingerprint_service.get_fingerprint_metadata(
        fingerprint_id
    )


# SUBJECT FROM FINGERPRINT
@router.get("/{fingerprint_id}/subject")
async def get_subject(
    fingerprint_id: int,
    user=Depends(get_current_user)
):
    return await fingerprint_service.get_fingerprint_subject(
        fingerprint_id
    )


# DELETE (ADMIN)
@router.delete("/{fingerprint_id}")
async def delete_fingerprint(
    fingerprint_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return await fingerprint_service.delete_fingerprint(
        fingerprint_id
    )