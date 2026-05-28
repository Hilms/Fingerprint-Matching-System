from app.db.database import database

from app.services.subject_service import SubjectService
from app.services.fingerprint_service import FingerprintService
from app.services.storage_service import StorageService
from app.services.import_service import ImportService
from app.services.user_service import UserService

from app.utils.fingerprint_embedder import FingerprintEmbedder

# shared service instances

user_service = UserService(database)

storage_service = StorageService()

subject_service = SubjectService(database)

fingerprint_embedder= FingerprintEmbedder()


fingerprint_service = FingerprintService(
    database=database,
    storage_service=storage_service,
    subject_service=subject_service,
    fingerprint_embedder=fingerprint_embedder,
)

import_service = ImportService(
    database=database,
    subject_service=subject_service,
    fingerprint_service=fingerprint_service,
    storage_service=storage_service
)

