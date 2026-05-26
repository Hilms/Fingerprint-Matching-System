class FingerprintService:

    def upload_fingerprint(
        self,
        file,
        subject_id: int,
        user
    ):

        # 1. validate user
        # 2. validate subject exists
        # 3. upload image to storage
        # 4. create fingerprint entry
        # 5. later create embedding

        return {
            "message": "fingerprint uploaded"
        }

    def delete_fingerprint(self, fingerprint_id: int):

        # 1. get fingerprint
        # 2. delete image from storage
        # 3. delete fingerprint from DB

        return {
            "message": f"fingerprint {fingerprint_id} deleted"
        }

    def search_fingerprints(self, query: str):

        # search metadata
        # search subject relation
        # return image info

        return []

    def get_fingerprint_metadata(
        self,
        fingerprint_id: int
    ):

        return {
            "id": fingerprint_id,
            "subject_id": 1,
            "image_path": "fingerprints/1/image.jpg"
        }

    def get_fingerprint_subject(
        self,
        fingerprint_id: int
    ):

        # later:
        # fingerprint -> subject_id
        # load subject

        return {
            "subject_id": 1,
            "name": "Max Mustermann"
        }
