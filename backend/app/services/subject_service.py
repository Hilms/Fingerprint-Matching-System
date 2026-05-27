from fastapi import HTTPException

class SubjectService:

    def __init__(self, db):
        self.db = db

    # CREATE
    async def create_subject(self, data: dict):

            # check if subject already exists
            existing = await self.get_subject_by_ref_id(
                data["external_id"]
            )

            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="subject already exists"
                )

            query = """
                INSERT INTO subjects (
                    external_id,
                    name,
                    age,
                    address,
                    city,
                    country,
                    has_fingerprint
                )
                VALUES (
                    :external_id,
                    :name,
                    :age,
                    :address,
                    :city,
                    :country,
                    TRUE
                )
                RETURNING *
            """

            subject = await self.db.fetch_one(
                query=query,
                values={
                    "external_id": data["external_id"],
                    "name": data["name"],
                    "age": data["age"],
                    "address": data["address"],
                    "city": data["city"],
                    "country": data["country"]
                }
            )

            return dict(subject)

    # DELETE
    async def delete_subject(
        self,
        subject_id: int
    ):
        # permanent delete
        # remove fingerprints
        # remove storage files
        # remove subject

        subject = await self.get_subject(subject_id)

        if not subject:
            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        # load fingerprints

        fingerprints_query = """
            SELECT *
            FROM fingerprints
            WHERE subject_id = :subject_id
        """

        fingerprints = await self.db.fetch_all(
            query=fingerprints_query,
            values={
                "subject_id": subject_id
            }
        )

        # delete storage files

        for fingerprint in fingerprints:

            try:
                self.fingerprint_service.storage_service.delete_image(
                    fingerprint["image_url"]
                )

            except Exception:
                pass

        async with self.db.transaction():

            # delete fingerprints

            delete_fingerprints_query = """
                DELETE FROM fingerprints
                WHERE subject_id = :subject_id
            """

            await self.db.execute(
                query=delete_fingerprints_query,
                    values={
                        "subject_id": subject_id
                    }
            )

            # delete subject

            delete_subject_query = """
                DELETE FROM subjects
                WHERE id = :subject_id
            """

            await self.db.execute(
                query=delete_subject_query,
                    values={
                        "subject_id": subject_id
                    }
            )

            return {
                "message": (
                    f"subject {subject_id} permanently deleted"
                )
            }


    # GET
    async def get_subject(
            self,
            subject_id: int
        ):

            query = """
                SELECT *
                FROM subjects
                WHERE id = :subject_id
            """

            subject = await self.db.fetch_one(
                query=query,
                values={
                    "subject_id": subject_id
                }
            )

            if not subject:
                return None

            return dict(subject)


    # SEARCH
    async def search_subjects(
        self,
        query: str
    ):

        search_query = """
            SELECT *
            FROM subjects
            WHERE
                name ILIKE :query
                OR city ILIKE :query
                OR country ILIKE :query
                OR CAST(external_id AS TEXT) ILIKE :query
        """

        subjects = await self.db.fetch_all(
            query=search_query,
            values={
                "query": f"%{query}%"
            }
        )

        return [
            dict(subject)
            for subject in subjects
        ]

    # UPDATE
    async def update_subject(
        self,
        subject_id: int,
        data: dict
    ):

        subject = await self.get_subject(
            subject_id
        )

        if not subject:

            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        update_query = """
            UPDATE subjects
            SET
                name = :name,
                age = :age,
                address = :address,
                city = :city,
                country = :country
            WHERE id = :subject_id
        """

        await self.db.execute(
            query=update_query,
            values={
                "subject_id": subject_id,
                "name": data["name"],
                "age": data["age"],
                "address": data["address"],
                "city": data["city"],
                "country": data["country"]
            }
        )

        return {
            "message": f"subject {subject_id} updated"
        }