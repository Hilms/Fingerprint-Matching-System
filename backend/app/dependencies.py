from app.db.database import database

from app.services.subject_service import SubjectService
from app.services.fingerprint_service import FingerprintService
from app.services.storage_service import StorageService
from app.services.import_service import ImportService

# shared service instances

storage_service = StorageService()

subject_service = SubjectService(database)

fingerprint_service = FingerprintService(
    database=database,
    storage_service=storage_service,
    subject_service=subject_service
)

import_service = ImportService(
    database = database,
    subject_service=subject_service,
    fingerprint_service=fingerprint_service,
    storage_service=storage_service
)