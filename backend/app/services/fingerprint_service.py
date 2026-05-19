class FingerprintService:

    def upload_fingerprint(self, file, subject_name: str, user):
        # 4. DB insert
        # 1. subject service
        # 2. storage service
        pass

    def delete_fingerprint(self, id: int):
        # DB delete
        # delete subject
        # storage delete
        pass

    def search_fingerprint(self, query: str):
        # DB search metadata
        # get subject
        # get image
        pass

    def get_metadata(self, id: int):
        pass

    def get_subject(self, id: int):
        pass