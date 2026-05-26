from fastapi import APIRouter, Depends

from app.security.auth import get_current_user
from app.security.permission import require_role

from app.services.import_service import ImportService
from app.services.storage_service import StorageService


router = APIRouter(
    prefix="/imports",
    tags=["imports"]
)

import_service = ImportService()
storage_service = StorageService()

# DATASET IMPORT
# ADMIN ONLY

@router.post("/dataset")
def import_dataset(
    user=Depends(get_current_user),
    _=Depends(require_role("admin"))
):

    return import_service.import_dataset(
        images_folder="dataset/images",
        subjects_file="dataset/subjects.csv",
        user=user
    )