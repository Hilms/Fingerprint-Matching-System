from pathlib import Path
import csv

from app.utils.fingerprint_parser import FingerprintParser


class ImportService:

    def __init__(
        self,
        database,
        storage_service,
        subject_service,
        fingerprint_service
    ):
        self.db = database
        self.storage_service = storage_service
        self.subject_service = subject_service
        self.fingerprint_service = fingerprint_service


    def load_subjects(self, csv_path: str):

        subjects = {}

        with open(csv_path, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                external_id = int(row["external_id"])

                subjects[external_id] = row

        return subjects


    async def import_data(
        self,
        subjects_csv: str,
        fingerprints_dir: str
    ):

        subjects = self.load_subjects(subjects_csv)

        fingerprint_files = Path(fingerprints_dir).glob("*.BMP")

        imported_subjects = 0
        imported_fingerprints = 0
        skipped_files = 0
        failed_files = 0

        fingerprint_parser = FingerprintParser()

        for file_path in fingerprint_files:

            filename = file_path.name

            meta = fingerprint_parser.parse_filename(filename)

            if meta is None:

                print(f"[SKIP] invalid filename: {filename}")

                skipped_files += 1
                continue

            external_id = int(meta["external_id"])

            subject_data = subjects.get(external_id)

            if not subject_data:

                print(f"[SKIP] no subject found for external_id={external_id}")

                skipped_files += 1
                continue

            try:

                # STORAGE
                image_url = self.storage_service.upload_image(
                    file=str(file_path),
                    object_path=filename
                )

                async with self.db.transaction():

                    # subject (create only if missing)
                    existing = await self.subject_service.get_subject(external_id)

                    if not existing:

                        await self.subject_service.create_subject({
                            "external_id": external_id,
                            "first_name": subject_data["first_name"],
                            "last_name": subject_data["last_name"],
                            "age": int(subject_data["age"]),
                            "address": subject_data["address"],
                            "city": subject_data["city"],
                            "country": subject_data["country"],
                            "phone_number": subject_data["phone_number"],
                            "has_fingerprints": False
                        })

                        imported_subjects += 1

                    embedding = self.fingerprint_service.create_embedding(file_path)

                    await self.fingerprint_service.create_fingerprint({
                        "subject_external_id": external_id,
                        "image_url": image_url,
                        "sex": meta["sex"],
                        "hand": meta["hand"],
                        "finger": meta["finger"],
                        "filename": filename,
                        "feature_vector": embedding
                    })

                imported_fingerprints += 1

                print(f"[OK] imported {filename}")

            except Exception as e:

                failed_files += 1

                print(f"[ERROR] {filename} -> {e}")

                try:
                    self.storage_service.delete_image(image_url)
                except Exception:
                    pass

        return {
            "message": "import finished",
            "subjects_created": imported_subjects,
            "fingerprints_created": imported_fingerprints,
            "skipped_files": skipped_files,
            "failed_files": failed_files
        }