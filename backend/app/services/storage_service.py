from app.storage.minio_client import minio_client, MINIO_BUCKET
from io import BytesIO
from datetime import timedelta

class StorageService:

    # UPLOAD
    def upload_image(self, file, object_path: str):

        # upload image to MinIO
        if hasattr(file, "file"):
            file_data = file.file
        else:
            # filepath reads
            file_data = open(file, "rb")

        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_path,
            data=file_data,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type="application/octet-stream"
        )

        return object_path

    # DELETE
    def delete_image(self, object_path: str):

        try:
            minio_client.remove_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_path
            )

            return {
                "message": "image deleted",
                "path": object_path
            }

        except Exception as e:
            return {
                "error": str(e),
                "path": object_path
            }


    def get_image(self, object_path: str):

        try:
            response = minio_client.get_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_path
            )

            # return response.read()
            return response

        except Exception as e:
            raise RuntimeError(f"Failed to fetch image from MinIO: {e}")


    # SIGNED URL TO IMAGE ? presigned URLs are failing because of a Docker hostname mismatch
    def get_signed_url(self, object_path: str):

        try:
            url = minio_client.presigned_get_object(
                bucket_name=MINIO_BUCKET,
                object_name=object_path,
                expires=timedelta(seconds=3600)
            )

            return {
                "url": url
            }

        except Exception as e:
            return {
                "error": str(e)
            }
