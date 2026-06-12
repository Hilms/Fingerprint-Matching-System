from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.dependencies import fingerprint_service

router = APIRouter(
    prefix="/fingerprints",
    tags=["fingerprints"]
)

ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/bmp"]


class FingerprintCreate(BaseModel):
    subject_external_id: int
    sex: str
    hand: str
    finger: str
    filename: str
    image_url: str
    feature_vector: str


@router.get("/all")
async def get_fingerprints(
    user=Depends(get_current_user)
):
    return await fingerprint_service.get_fingerprints()

@router.get("/image/{filename}")
async def get_fingerprint_img(
    filename: str,
    user=Depends(get_current_user)
):
    return await fingerprint_service.get_fingerprint_img(filename)


# SEARCH
@router.get("/search")
async def search_fingerprints(
    query: str,
    user=Depends(get_current_user)
):

    return await fingerprint_service.search_fingerprints(query)

@router.get("/id/{external_id}")
async def get_fingerprints_by_subject_id(
    external_id: int,
    user=Depends(get_current_user)
):
    return await fingerprint_service.get_fingerprints_by_subject_id(external_id)

# METADATA
@router.get("/metadata/id/{fingerprint_id}")
async def get_metadata(
    fingerprint_id: int,
    user=Depends(get_current_user)
):

    return await fingerprint_service.get_fingerprint_metadata(
        fingerprint_id
    )


@router.get("/subject/id/{subject_external_id}")
async def get_subject_fingerprint(
    subject_external_id: int,
    user=Depends(get_current_user)
):

    return await fingerprint_service.get_fingerprint_subject(
        subject_external_id
    )


# GET SUBJECT & FINGERPRINT FOR MATCHING
@router.get("/fingerprint_subject/id/{subject_external_id}")
async def get_fingerprint_subject(
    subject_external_id: int,
    user=Depends(get_current_user)
):

    return await fingerprint_service.get_fingerprint_subject(
        subject_external_id
    )


# MATCH FINGERPRINT
@router.post("/match")
async def match_fingerprint(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )

    return await fingerprint_service.match_fingerprint(file=file)


# UPLOAD (subject + fingerprint in one step)
@router.post("/admin/upload")
async def upload_fingerprint(
    external_id: int,
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
        file=file,
        external_id=external_id
    )


# MANUAL CREATE FINGERPRINT (import / UI use case)
@router.post("/admin/create")
async def create_fingerprint(
    data: FingerprintCreate,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    return await fingerprint_service.create_fingerprint(
        data.dict()
    )


#DELETE
@router.delete("/admin/delete/id/{fingerprint_id}")
async def delete_fingerprint(
    fingerprint_id: int,
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    return await fingerprint_service.delete_fingerprint(
        fingerprint_id
    )


