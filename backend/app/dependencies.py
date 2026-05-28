from app.db.database import database

from app.services.subject_service import SubjectService
from app.services.fingerprint_service import FingerprintService
from app.services.storage_service import StorageService
from app.services.import_service import ImportService
from app.services.user_service import UserService

from app.matching.fingerprint_embedder import FingerprintEmbedder
from app.matching.fingerprint_minutiae_matcher import FingerprintMinutiaeMatcher

# shared service instances

user_service = UserService(database)

storage_service = StorageService()

subject_service = SubjectService(database)

fingerprint_embedder= FingerprintEmbedder()

fingerprint_minutiae_matcher = FingerprintMinutiaeMatcher(
    minutiae_embedder=fingerprint_embedder.minutiae_embedder
)


fingerprint_service = FingerprintService(
    database=database,
    storage_service=storage_service,
    subject_service=subject_service,
    fingerprint_embedder=fingerprint_embedder,
    fingerprint_minutiae_matcher=fingerprint_minutiae_matcher
)

import_service = ImportService(
    database=database,
    subject_service=subject_service,
    fingerprint_service=fingerprint_service,
    storage_service=storage_service
)

