import os
from fastapi import APIRouter, Depends

from app.security.auth import get_current_user
from app.security.permission import require_role
from app.dependencies import import_service

router = APIRouter(prefix="/imports", tags=["imports"])

SUBJECTS_CSV_PATH = os.getenv("IMPORT_SUBJECTS_CSV_PATH")
FINGERPRINTS_DIR_PATH = os.getenv("IMPORT_FINGERPRINTS_DIR_PATH")


@router.post("/admin/dataset")
async def import_data(
    _=Depends(require_role("admin"))
):
    return await import_service.import_data(
        subjects_csv=SUBJECTS_CSV_PATH,
        fingerprints_dir=FINGERPRINTS_DIR_PATH
    )


