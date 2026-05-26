from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.services.fingerprint_service import FingerprintService
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/fingerprints",
    tags=["fingerprints"]
)

fingerprint_service = FingerprintService()
storage_service = StorageService()

@router.post("/upload")
def upload_fingerprint(
    subject_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return fingerprint_service.upload_fingerprint(
        file,
        subject_id,
        user
    )

@router.get("/search")
def search_fingerprints(
    q: str,
    user=Depends(get_current_user)
):
    return fingerprint_service.search_fingerprints(q)

@router.get("/{fingerprint_id}")
def get_metadata(
    fingerprint_id: int,
    user=Depends(get_current_user)
):
    return fingerprint_service.get_fingerprint_metadata(
        fingerprint_id
    )

@router.get("/{fingerprint_id}/subject")
def get_subject(
    fingerprint_id: int,
    user=Depends(get_current_user)
):
    return fingerprint_service.get_fingerprint_subject(
        fingerprint_id
    )

@router.delete("/{fingerprint_id}")
def delete_fingerprint(
    fingerprint_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):
    return fingerprint_service.delete_fingerprint(
        fingerprint_id
    )