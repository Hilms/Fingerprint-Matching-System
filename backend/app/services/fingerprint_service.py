from fastapi import HTTPException
import cv2
import numpy as np

from app.utils.fingerprint_parser import FingerprintParser


class FingerprintService:

    def __init__(
        self,
        database,
        storage_service,
        subject_service,
        fingerprint_embedder,
        fingerprint_minutiae_matcher,
        embedding_method="correlation"
    ):

        self.db = database
        self.storage_service = storage_service
        self.subject_service = subject_service
        self.fingerprint_embedder = fingerprint_embedder
        self.embedding_method = embedding_method
        self.fingerprint_minutiae_matcher = fingerprint_minutiae_matcher


    def load_image(self, source):
        #  --> currently passing raw bytes

        # upload file case
        if hasattr(source, "file"):

            file_bytes = source.file.read()

            image_array = np.frombuffer(
                file_bytes,
                np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_GRAYSCALE
            )

            source.file.seek(0)

            return image

        # raw bytes case (file.file)
        if isinstance(source, (bytes, bytearray)):
            image_array = np.frombuffer(source, np.uint8)
            return cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

        # file path case
        return cv2.imread(source, cv2.IMREAD_GRAYSCALE)


    def create_embedding(self, source):

        image = self.load_image(source)

        if image is None:

            raise HTTPException(
                status_code=400,
                detail="invalid fingerprint image"
            )

        vec = self.fingerprint_embedder.extract_embedding(
            image,
            self.embedding_method
        )

        # format for storing vector in db
        return "[" + ",".join(str(x) for x in vec) + "]"

    # UPLOAD
    async def upload_fingerprint(
        self,
        file=None,
        external_id: int = None,
        subject_data: dict = None
    ):

        # resolve subject (existing or create new)
        subject = None

        if external_id:
            # case existing subject + fingerprint upload
            subject = await self.subject_service.get_subject(
                external_id
            )

            if not subject:

                raise HTTPException(
                    status_code=404,
                    detail="subject not found"
                )

        elif subject_data:
            # case new subject (fingerprint optional)
            subject = await self.subject_service.create_subject(
                subject_data
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="external_id or subject_data required"
            )

        # subject only flow
        # create subject without fingerprint
        if file is None:

            return {
                "message": "subject created",
                "subject": subject
            }

        # case (new)subject and fingerprint
        filename = file.filename
        file_bytes = file.file.read()

        fingerprint_parser = FingerprintParser()

        meta = fingerprint_parser.parse_filename(
            filename
        )

        if meta is None:

            raise HTTPException(
                status_code=400,
                detail="invalid filename format"
            )

        # compute embedding
        embedding = self.create_embedding(file_bytes)

        # check duplicate fingerprints
        existing_fingerprint = await self.find_duplicate_fingerprint(
            embedding
        )

        if existing_fingerprint:

            raise HTTPException(
                status_code=409,
                detail=(
                    "similar fingerprint already exists "
                    f"(fingerprint_id={existing_fingerprint['id']})"
                )
            )

        image_url = None

        try:

            # upload image to storage
            file.file.seek(0)
            image_url = self.storage_service.upload_image(
                file=file,
                object_path=filename
            )

            # DB transaction

            async with self.db.transaction():

                # create fingerprint entry

                fingerprint = await self.create_fingerprint({
                    "subject_external_id": subject["external_id"],
                    "image_url": image_url,
                    "sex": meta["sex"],
                    "hand": meta["hand"],
                    "finger": meta["finger"],
                    "filename": filename,
                    "feature_vector": embedding
                })

            return {
                "message": "fingerprint uploaded",
                "subject": subject,
                "fingerprint": fingerprint
            }

        except Exception as e:

            # rollback storage manually
            if image_url:

                try:
                    self.storage_service.delete_image(image_url)

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

        query = """
            INSERT INTO fingerprints (
                subject_external_id,
                image_url,
                sex,
                hand,
                finger,
                filename,
                feature_vector
            )
            VALUES (
                :subject_external_id,
                :image_url,
                :sex,
                :hand,
                :finger,
                :filename,
                CAST(:feature_vector as vector)
            )
            RETURNING *
        """

        fingerprint = await self.db.fetch_one(
            query=query,
            values={
                "subject_external_id": data["subject_external_id"],
                "image_url": data["image_url"],
                "sex": data["sex"],
                "hand": data["hand"],
                "finger": data["finger"],
                "filename": data["filename"],
                "feature_vector": data["feature_vector"]
            }
        )

        await self.db.execute(
            query="""
                UPDATE subjects
                SET has_fingerprints = TRUE
                WHERE external_id = :external_id
                  AND has_fingerprints = FALSE
            """,
            values={
                "external_id": data["subject_external_id"]
            }
        )

        return dict(fingerprint)

    # GET
    async def get_fingerprints(self):

        query = """
            SELECT *
            FROM fingerprints
            ORDER BY subject_external_id
        """

        fingerprints = await self.db.fetch_all(query)

        return [
            dict(fingerprint)
            for fingerprint in fingerprints
        ]

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
            WHERE subject_external_id = :subject_external_id
        """

        remaining = await self.db.fetch_one(
            query=count_query,
            values={
                "subject_external_id": fingerprint["subject_external_id"]
            }
        )

        # deactivate subject if no fingerprints left

        if remaining["count"] == 0:

            update_query = """
                UPDATE subjects
                SET has_fingerprints = FALSE
                WHERE external_id = :external_id
            """

            await self.db.execute(
                query=update_query,
                values={
                    "external_id": fingerprint["subject_external_id"]
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
                f.subject_external_id,
                f.image_url,
                f.sex,
                f.hand,
                f.finger,
                f.filename,
                s.first_name,
                s.last_name,
                s.city,
                s.country
            FROM fingerprints f
            JOIN subjects s
                ON f.subject_external_id = s.external_id
            WHERE
                LOWER(s.first_name) LIKE LOWER(:query)
                OR LOWER(s.last_name) LIKE LOWER(:query)
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
        subject_external_id: int
    ):

        query = """
            SELECT *
            FROM subjects
            WHERE external_id = :subject_external_id
        """

        subject = await self.db.fetch_one(
            query=query,
            values={
                "subject_external_id": subject_external_id
            }
        )

        if not subject:
            raise HTTPException(
                status_code=404,
                detail="subject not found"
            )

        return dict(subject)


    async def find_duplicate_fingerprint(
        self,
        embedding: list[float],
        threshold: float = 0.05
    ):

        query = """
            SELECT
                id,
                subject_external_id,
                filename,
                feature_vector <-> CAST(:embedding as vector) AS distance
            FROM fingerprints
            ORDER BY distance ASC
            LIMIT 1
        """

        result = await self.db.fetch_one(
            query=query,
            values={
                "embedding": embedding
            }
        )

        if not result:
            return None

        result = dict(result)

        # duplicate detected
        if result["distance"] <= threshold:
            return result

        return None


    async def match_fingerprint(
        self,
        file,
        k: int = 5
    ):

        # load fingerprint image
        # create retrieval embedding
        # this embedding is used only for:
        # pgvector similarity retrieval
        file_bytes = file.file.read()
        file.file.seek(0)

        embedding = self.create_embedding(file_bytes)

        # search nearest fingerprint candidates
        query = """
            SELECT
                id,
                subject_external_id,
                image_url,
                filename,
                feature_vector <-> CAST(:embedding as vector) AS distance
            FROM fingerprints
            ORDER BY distance ASC
            LIMIT :k
        """

        candidates = await self.db.fetch_all(
            query=query,
            values={
                "embedding": embedding,
                "k": k
            }
        )

        if not candidates:
            return []

        # download candidate images

        candidate_images = []

        for candidate in candidates:

            candidate = dict(candidate)

            try:

                # retrieve image bytes from storage

                try:
                    image_bytes = self.storage_service.get_image(candidate["image_url"])
                except Exception:
                    continue

                # convert bytes -> opencv image
                image_array = np.frombuffer(
                    image_bytes,
                    np.uint8
                )

                candidate_image = cv2.imdecode(
                    image_array,
                    cv2.IMREAD_GRAYSCALE
                )

                if candidate_image is None:
                    continue

                candidate_images.append({
                    "id": candidate["id"],
                    "subject_external_id": candidate["subject_external_id"],
                    "image": candidate_image
                })

            except Exception:
                continue


        # minutiae verification
        query_image = self.load_image(file_bytes)

        results = self.fingerprint_minutiae_matcher.match_candidates(
            query_image,
            candidate_images
        )

        # enrich results with:
        # fingerprint metadata
        # subject information

        enriched_results = []

        subject_cache = {}

        for result in results:

            fingerprint_metadata = await self.get_fingerprint_metadata(
                result["candidate_id"]
            )

            subject_external_id = result["subject_external_id"]

            # CACHE SUBJECT LOOKUP (avoid repeated DB calls)
            if subject_external_id not in subject_cache:
                subject_cache[subject_external_id] = await self.get_fingerprint_subject(
                    subject_external_id
                )

            subject = subject_cache[subject_external_id]

            enriched_results.append({
                "fingerprint": fingerprint_metadata,
                "subject": subject,
                "accuracy": result["accuracy"],
                "total_matches": result["total_matches"],
                "query_minutiae_count": result["query_minutiae_count"],
                "candidate_minutiae_count": result["candidate_minutiae_count"],
                "matched_points": result["matched_points"]
            })

        return enriched_results

    async def get_by_filename(self, filename: str):
        query = """
            SELECT id
            FROM fingerprints
            WHERE filename = :filename
            LIMIT 1
        """

        result = await self.db.fetch_one(
            query=query,
            values={"filename": filename}
        )

        return result is not None