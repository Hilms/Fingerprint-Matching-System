from fastapi import HTTPException
from app.utils.fingerprint_parser import parse_filename

class FingerprintService:

    def __init__(
        self,
        database,
        storage_service,
        subject_service
    ):
        self.db = database
        self.storage_service = storage_service
        self.subject_service = subject_service

    # UPLOAD
    async def upload_fingerprint(
        self,
        file,
        user,
        subject_id: int = None,
        subject_data: dict = None
    ):

        # validate filename

        filename = file.filename

        meta = parse_filename(filename)

        if meta is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "invalid filename format. "
                    "expected: "
                    "1__M_Left_thumb_finger.BMP"
                )
            )

        # create subject OR load existing subject

        subject = None

        # existing subject flow
        if subject_id:

            subject = await self.subject_service.get_subject(
                subject_id
            )

            if not subject:

                raise HTTPException(
                    status_code=404,
                    detail="subject not found"
                )

        # new subject flow
        elif subject_data:

            subject = await self.subject_service.create_subject(
                subject_data
            )

        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "subject_id or subject_data required"
                )
            )

        # later:
        # extract fingerprint embedding/vector

        # placeholder embedding
        feature_vector = [0.0] * 128

        # check if fingerprint already exists

        # placeholder duplicate check
        existing_fingerprint = None

        if existing_fingerprint:

            raise HTTPException(
                status_code=409,
                detail="fingerprint already exists"
            )

        object_path = f"fingerprints/{filename}"

        try:

            # upload image to storage

            image_url = self.storage_service.upload_image(
                file=file,
                object_path=object_path
            )

            # DB transaction

            async with self.db.transaction():

                # create fingerprint entry

                fingerprint = await self.create_fingerprint({
                    "subject_id": subject["id"],
                    "image_url": image_url,
                    "sex": meta["sex"],
                    "hand": meta["hand"],
                    "finger": meta["finger"],
                    "filename": filename,
                    "feature_vector": feature_vector
                })

                # activate subject
                # important:
                # if subject had no fingerprints before,
                # set active = TRUE

                activate_query = """
                    UPDATE subjects
                    SET has_fingerprints = TRUE
                    WHERE id = :subject_id
                """

                await self.db.execute(
                    query=activate_query,
                    values={
                        "subject_id": subject["id"]
                    }
                )

            return {
                "message": "fingerprint uploaded",
                "subject": subject,
                "fingerprint": fingerprint
            }

        except Exception as e:

            # rollback storage manually

            try:

                self.storage_service.delete_image(
                    object_path
                )

            except Exception:
                pass

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    # CREATE
    async def create_fingerprint(
        self,
        data: dict
    ):

        # 1. insert DB record
        # 2. later add embedding

        query = """
            INSERT INTO fingerprints (
                subject_id,
                image_url,
                sex,
                hand,
                finger,
                filename
            )
            VALUES (
                :subject_id,
                :image_url,
                :sex,
                :hand,
                :finger,
                :filename
            )
            RETURNING *
        """

        fingerprint = await self.db.fetch_one(
            query=query,
            values={
                "subject_id": data["subject_id"],
                "image_url": data["image_url"],
                "sex": data["sex"],
                "hand": data["hand"],
                "finger": data["finger"],
                "filename": data["filename"]
            }
        )

        return dict(fingerprint)


    # DELETE
    async def delete_fingerprint(
        self,
        fingerprint_id: int
    ):

        # get fingerprint

        fingerprint = await self.get_fingerprint_metadata(
            fingerprint_id
        )

        if not fingerprint:
            raise HTTPException(
                status_code=404,
                detail="fingerprint not found"
            )

        # delete image from storage

        self.storage_service.delete_image(
            fingerprint["image_url"]
        )

        # delete fingerprint from DB

        query = """
            DELETE FROM fingerprints
            WHERE id = :fingerprint_id
        """

        await self.db.execute(
            query=query,
            values={
                "fingerprint_id": fingerprint_id
            }
        )

        # check remaining fingerprints

        count_query = """
            SELECT COUNT(*) as count
            FROM fingerprints
            WHERE subject_id = :subject_id
        """

        remaining = await self.db.fetch_one(
            query=count_query,
            values={
                "subject_id": subject_id
            }
        )

        # deactivate subject if no fingerprints left

        if remaining["count"] == 0:

            update_query = """
                UPDATE subjects
                SET has_fingerprints = FALSE
                WHERE id = :subject_id
            """

            await self.db.execute(
                query=update_query,
                values={
                    "subject_id": subject_id
                }
            )

        return {
            "message": f"fingerprint {fingerprint_id} deleted"
        }


    # SEARCH
    async def search_fingerprints(
        self,
        query: str
    ):

        # search metadata
        # search subject relation
        # return image info

        sql = """
            SELECT
                f.id,
                f.subject_id,
                f.image_url,
                f.sex,
                f.hand,
                f.finger,
                f.filename,
                s.name,
                s.city,
                s.country
            FROM fingerprints f
            JOIN subjects s
                ON f.subject_id = s.id
            WHERE
                LOWER(s.name) LIKE LOWER(:query)
                OR LOWER(s.city) LIKE LOWER(:query)
                OR LOWER(s.country) LIKE LOWER(:query)
                OR LOWER(f.filename) LIKE LOWER(:query)
                OR LOWER(f.finger) LIKE LOWER(:query)
        """

        fingerprints = await self.db.fetch_all(
            query=sql,
            values={
                "query": f"%{query}%"
            }
        )

        return [
            dict(fingerprint)
            for fingerprint in fingerprints
        ]


    # SEARCH
    async def get_fingerprint_metadata(
        self,
        fingerprint_id: int
    ):

        query = """
            SELECT *
            FROM fingerprints
            WHERE id = :fingerprint_id
        """

        fingerprint = await self.db.fetch_one(
            query=query,
            values={
                "fingerprint_id": fingerprint_id
            }
        )

        if not fingerprint:
            return None

        return dict(fingerprint)


    async def get_fingerprint_subject(
        self,
        fingerprint_id: int
    ):

        query = """
            SELECT s.*
            FROM fingerprints f
            JOIN subjects s
                ON f.subject_id = s.id
            WHERE f.id = :fingerprint_id
        """

        subject = await self.db.fetch_one(
            query=query,
            values={
                "fingerprint_id": fingerprint_id
            }
        )

        if not subject:
            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        return dict(subject)