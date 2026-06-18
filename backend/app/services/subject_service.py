from fastapi import HTTPException


class SubjectService:

    def __init__(self, db, storage_service=None):
        self.db = db
        self.storage_service = storage_service

    async def subject_exists_by_external_id(self, external_id: int) -> bool:
        query = """
            SELECT 1
            FROM subjects
            WHERE external_id = :external_id
        """

        result = await self.db.fetch_one(
            query=query,
            values={"external_id": external_id}
        )

        return result is not None


    # CREATE
    async def create_subject(self, data: dict):

        # check if subject already exists
        existing = await self.subject_exists_by_external_id(
            int(data["external_id"])
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="subject already exists"
            )

        query = """
            INSERT INTO subjects (
                external_id,
                first_name,
                last_name,
                age,
                address,
                city,
                country,
                phone_number,
                has_fingerprints
            )
            VALUES (
                :external_id,
                :first_name,
                :last_name,
                :age,
                :address,
                :city,
                :country,
                :phone_number,
                :has_fingerprints
            )
            RETURNING *
        """

        subject = await self.db.fetch_one(
            query=query,
            values={
                "external_id": int(data.get("external_id")),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "age": data.get("age"),
                "address": data.get("address"),
                "city": data.get("city"),
                "country": data.get("country"),
                "phone_number": data.get("phone_number"),
                "has_fingerprints": data.get("has_fingerprints")
            }
        )

        return dict(subject)


    # GET
    async def get_subject(
            self,
            external_id: int
        ):

        query = """
            SELECT *
            FROM subjects
            WHERE external_id = :external_id
        """

        subject = await self.db.fetch_one(
            query=query,
            values={
                "external_id": external_id
            }
        )

        if not subject:
            return None

        return dict(subject)


    async def get_subjects(self):

        query = """
            SELECT *
            FROM subjects
            ORDER BY external_id
        """

        subjects = await self.db.fetch_all(query)

        return [
            dict(subject)
            for subject in subjects
        ]

    async def get_latest_subject_id(self):

        query = """
            SELECT external_id
            FROM subjects
            ORDER BY external_id DESC
            LIMIT 1
        """

        row = await self.db.fetch_one(query)

        if not row:
            return {"latest_subject_id": None}

        return {
            "latest_subject_id" : row["external_id"]
        }


    # SEARCH
    async def search_subjects(
        self,
        query: str
    ):

        sql = """
            SELECT *
            FROM subjects
            WHERE
                first_name ILIKE :query
                OR last_name ILIKE :query
                OR city ILIKE :query
                OR country ILIKE :query
                OR CAST(external_id AS TEXT) ILIKE :query
            ORDER BY external_id
        """

        subjects = await self.db.fetch_all(
            query=sql,
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
        external_id: int,
        data: dict
    ):

        # check subject exists
        subject_exists = await self.subject_exists_by_external_id(
            external_id
        )

        if not subject_exists:
            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        try:

            update_fields = []

            values = {
                "external_id": external_id
            }

            allowed_fields = [
                "first_name",
                "last_name",
                "age",
                "address",
                "city",
                "country",
                "phone_number",
                "has_fingerprints"
            ]

            for field in allowed_fields:

                if field in data and data[field] is not None:

                    update_fields.append(
                        f"{field} = :{field}"
                    )

                    values[field] = data[field]

            if not update_fields:

                return {
                    "message": "nothing to update"
                }

            query = f"""
                UPDATE subjects
                SET {", ".join(update_fields)}
                WHERE external_id = :external_id
            """

            async with self.db.transaction():

                await self.db.execute(
                    query=query,
                    values=values
                )

            return {
                "success" : True,
                "message": f"subject {external_id} updated"
                }

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


    # DELETE
    async def delete_subject(
        self,
        external_id: int
    ):

        # permanent delete
        # remove fingerprints
        # remove storage files
        # remove subject

        subject_exists = await self.subject_exists_by_external_id(
            external_id
        )

        if not subject_exists:
            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        try:

            # load fingerprints
            # needed to retrieve image urls before deletion

            fingerprints = await self.db.fetch_all(
                query="""
                    SELECT image_url
                    FROM fingerprints
                    WHERE subject_external_id = :external_id
                """,
                values={
                    "external_id": external_id
                }
            )

            # delete subject
            # fingerprints are deleted automatically
            # via ON DELETE CASCADE

            async with self.db.transaction():

                await self.db.execute(
                    query="""
                        DELETE FROM subjects
                        WHERE external_id = :external_id
                    """,
                    values={
                        "external_id": external_id
                    }
                )

            # delete storage files
            # done after successful db deletion
            # avoids broken db references if transaction fails

            if fingerprints:

                for fingerprint in fingerprints:

                    try:

                        self.storage_service.delete_image(
                            fingerprint["image_url"]
                        )

                    except Exception:

                        # ignore individual storage failures
                        # db has already been cleaned up

                        pass

            return {
                "success" : True,
                "message": f"subject {external_id} and corresponding fingerprints successfully deleted"
            }

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )