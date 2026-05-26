class StorageService:

    def upload_image(
        self,
        file,
        object_path: str
    ):

        # upload image to MinIO

        return {
            "message": "image uploaded",
            "path": object_path
        }

    def delete_image(
        self,
        object_path: str
    ):

        # delete image from MinIO

        return {
            "message": "image deleted",
            "path": object_path
        }

    def get_image(
        self,
        object_path: str
    ):

        # later:
        # return image stream/file

        return {
            "path": object_path
        }

    def get_signed_url(
        self,
        object_path: str
    ):

        # later:
        # create signed MinIO URL

        return {
            "url": f"/storage/{object_path}"
        }
