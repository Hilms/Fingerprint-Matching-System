class ImportService:

    def import_dataset(
        self,
        images_folder,
        subjects_file,
        user
    ):

        # 1. parse subject file
        # 2. iterate image folder
        # 3. create subjects
        # 4. upload images
        # 5. create fingerprint entries

        return {
            "message": "dataset imported",
            "imported_by": user["username"]
        }
