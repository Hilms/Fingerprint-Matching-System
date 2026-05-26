from pathlib import Path
import csv
import re

class ImportService:

    def __init__(self, database, storage_service, subject_service, fingerprint_service):

        self.db = database
        self.storage_service = storage_service
        self.subject_service = subject_service
        self.fingerprint_service = fingerprint_service



    FILENAME_PATTERN = re.compile(
        r"^(\d+)__(M|F)_(Left|Right)_(thumb|index|middle|ring|little)_finger\.BMP$",
        re.IGNORECASE
    )

    def parse_filename(self, filename: str):

        if not self.FILENAME_PATTERN.match(filename):
            return None

        # remove extension
        name = Path(filename).stem

        # split
        parts = name.split("_")

        # 1__M_Left_thumb_finger
        # ['1', '', 'M', 'Left', 'thumb', 'finger']

        external_id = int(parts[0])

        sex = parts[2]

        hand = parts[3].lower()

        finger = parts[4].lower()

        return {
            "external_id": external_id,
            "sex": sex,
            "hand": hand,
            "finger": finger
        }


    def load_subjects(self, csv_path: str):

        subjects = {}

        with open(csv_path, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                external_id = int(row["external_id"])

                subjects[external_id] = row

        return subjects

    async def import_data(self, subjects_csv: str, fingerprints_dir: str):

        subjects = self.load_subjects(subjects_csv)
        fingerprint_files = Path(fingerprints_dir).glob("*.BMP")

        for file_path in fingerprint_files:

            filename = file_path.name

            # validate filename
            meta = self.parse_filename(filename)

            if meta is None:
                print(f"[SKIP] invalid filename: {filename}")
                continue

            external_id = meta["external_id"]
            subject_data = subjects.get(external_id)

            if not subject_data:
                print(f"[SKIP] no subject for external_id: {external_id}")
                continue

            uploaded_image_path = f"fingerprints/{filename}"

            try:
                # STORAGE
                image_url = self.storage_service.upload_image(
                    file=str(file_path),
                    path=uploaded_image_path
                )

                # DB TRANSACTION
                async with self.db.transaction():

                    subject = await self.subject_service.create_subject({
                        "external_id": external_id,
                        "name": subject_data["name"],
                        "age": subject_data["age"],
                        "address": subject_data["address"],
                        "city": subject_data["city"],
                        "country": subject_data["country"]
                    })

                    fingerprint = await self.fingerprint_service.create_fingerprint({
                        "subject_id":subject["id"],
                        "image_url":image_url,
                        "sex":meta["sex"],
                        "hand":meta["hand"],
                        "finger":meta["finger"],
                        "filename":filename
                    })

                print(f"[OK] imported: {filename}")

            except Exception as e:

                print(f"[ERROR] failed: {filename} -> {e}")

                # rollback storage ONLY if file exists
                try:
                    self.storage_service.delete_image(uploaded_image_path)
                    print(f"[ROLLBACK] deleted: {uploaded_image_path}")
                except Exception as se:
                    print(f"[ROLLBACK FAILED] {uploaded_image_path} -> {se}")