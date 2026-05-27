from fastapi import HTTPException

class SubjectService:

    def __init__(self, db):
        self.db = db

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

    async def delete_subject(self, subject_id: int):

        # later:
        # delete fingerprints first
        # delete storage files
        # delete subject

        return {
            "message": f"subject {subject_id} deleted"
        }

    async def get_subject(self, subject_id: int):

        # later:
        # select * from subjects where id=...

        return {
            "id": subject_id,
            "ref_id": "SUB-001",
            "name": "Max Mustermann",
            "age": 32,
            "address": "Main Street 1",
            "city": "Frankfurt",
            "country": "Germany"
        }

    async def get_subject_by_ref_id(self, ref_id: str):

        # later db query

        return None

    async def search_subjects(self, query: str):

        # later:
        # search by:
        # name
        # city
        # country
        # ref_id

        return [
            {
                "id": 1,
                "name": "Max Mustermann",
                "city": "Frankfurt"
            }
        ]

    async def update_subject(
        self,
        subject_id: int,
        data: dict
    ):

        # later update query

        return {
            "message": f"subject {subject_id} updated"
        }