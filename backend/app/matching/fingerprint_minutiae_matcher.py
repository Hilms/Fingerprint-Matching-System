import math

class FingerprintMinutiaeMatcher:
    """
    performs geometric fingerprint verification
    using minutiae extracted from fingerprint images

    # IMPORTANT
    this class does NOT implement embeddings, they are already handled by:
        FingerprintEmbedder

    this matcher ONLY:
        - get minutiae embeddings from images
        - aligns minutiae geometrically
        - finds corresponding minutiae
        - computes similarity score
        - returns matching locations

    # PURPOSE

        This class compares:

        uploaded fingerprint
                    VS
        candidate fingerprints

        using:
            - minutiae extraction
            - geometric alignment
            - minutiae correspondence

    ----------------------------------------------------------

    # WHY THIS CLASS EXISTS

    vector embeddings are good for:
        - fast search & retrieval
        - pgvector

    but final biometric verification requires:
        - geometric matching
        - spatial alignment
        - minutiae correspondence

    this class performs that final verification
    """

    def __init__(
        self,
        minutiae_embedder,
        distance_threshold=15,
        angle_threshold=20
    ):

        """
        distance_threshold:
            maximum allowed spatial distance between minutiae

        angle_threshold:
            maximum allowed orientation difference
        """

        self.distance_threshold = distance_threshold
        self.angle_threshold = angle_threshold
        self.minutiae_embedder = minutiae_embedder


    def match_candidates(
            self,
            query_image,
            candidates
        ):


            query_minutiae = self.minutiae_embedder(query_image)

            results = []

            for candidate in candidates:

                candidate_id = candidate["id"]

                candidate_image = candidate["image"]

                # extract candidate minutiae
                candidate_minutiae = (
                    self.minutiae_embedder(
                        candidate_image
                    )
                )

                if (
                    len(query_minutiae) == 0 or
                    len(candidate_minutiae) == 0
                ):
                    continue


                # align candidate minutiae, take n points find best alignment
                aligned_candidate = self.best_alignment_minutiae(
                    query_minutiae,
                    candidate_minutiae,
                    top_n=5
                )

                # find matching points
                matched_points = self.find_matches(
                        query_minutiae,
                        aligned_candidate
                    )

                # compute match score
                total_possible = max(
                    len(query_minutiae),
                    len(candidate_minutiae)
                )

                accuracy = (
                    len(matched_points) /
                    total_possible
                )

                # filter out matchings under 80%
                if accuracy > 0.8:
                    results.append({
                        "candidate_id": candidate_id,
                        "subject_external_id": candidate.get("subject_external_id"),
                        "accuracy": accuracy,
                        "total_matches": len(matched_points),
                        "query_minutiae_count": len(query_minutiae),
                        "candidate_minutiae_count": len(candidate_minutiae),
                        # used later for visualization
                        "matched_points": matched_points
                    })


            # sort by best match
            results = sorted(
                results,
                key=lambda x: x["accuracy"],
                reverse=True
            )

            return results

    def best_alignment_minutiae(
        self,
        query_minutiae,
        candidate_minutiae,
        top_n: int = 5
    ):

        candidate_refs = candidate_minutiae[:top_n]
        query_ref = query_minutiae[0]

        best_score = 0
        best_aligned = None

        for ref_c in candidate_refs:

            rotation_angle = math.radians(
                query_ref["angle"] - ref_c["angle"]
            )

            cos_theta = math.cos(rotation_angle)
            sin_theta = math.sin(rotation_angle)

            aligned = []

            for minutia in candidate_minutiae:

                rel_x = minutia["x"] - ref_c["x"]
                rel_y = minutia["y"] - ref_c["y"]

                rotated_x = rel_x * cos_theta - rel_y * sin_theta
                rotated_y = rel_x * sin_theta + rel_y * cos_theta

                aligned.append({
                    "x": rotated_x + query_ref["x"],
                    "y": rotated_y + query_ref["y"],
                    "angle": minutia["angle"] + math.degrees(rotation_angle),
                    "type": minutia["type"]
                })

                matched = self.find_matches(query_minutiae, aligned)

                score = len(matched) / max(len(query_minutiae), len(candidate_minutiae))

                if score > best_score:
                    best_score = score
                    best_aligned = aligned

        return best_aligned


    def align_minutiae(
        self,
        query_minutiae,
        candidate_minutiae
    ):

        """
        align candidate fingerprint to query fingerprint
        using:

            1. rotation
            2. translation

        drawback: only one point of reference
        """

        query_ref = query_minutiae[0]

        candidate_ref = candidate_minutiae[0]

        # rotation
        rotation_angle = math.radians(

            query_ref["angle"] -

            candidate_ref["angle"]
        )

        cos_theta = math.cos(rotation_angle)

        sin_theta = math.sin(rotation_angle)

        aligned = []

        # rotate around candidate reference

        for minutia in candidate_minutiae:

            # shift to origin
            rel_x = (
                minutia["x"] -
                candidate_ref["x"]
            )

            rel_y = (
                minutia["y"] -
                candidate_ref["y"]
            )

            # apply rotation

            rotated_x = (
                rel_x * cos_theta -
                rel_y * sin_theta
            )

            rotated_y = (
                rel_x * sin_theta +
                rel_y * cos_theta
            )

            # translate to query position

            final_x = (
                rotated_x +
                query_ref["x"]
            )

            final_y = (
                rotated_y +
                query_ref["y"]
            )

            aligned.append({

                "x": final_x,

                "y": final_y,

                "type": minutia["type"],

                # rotate angle too
                "angle": (
                    minutia["angle"] +
                    math.degrees(rotation_angle)
                )
            })

        return aligned


    def find_matches(
        self,
        query_minutiae,
        candidate_minutiae
    ):

        # find corresponding minutiae pairs.

        matches = []

        # prevents one candidate minutia
        # from matching multiple query minutiae
        used_candidate = set()

        for query_point in query_minutiae:

            # search
            for idx, candidate_point in enumerate(
                candidate_minutiae
            ):

                # already used
                if idx in used_candidate:
                    continue

               # type check

                if (
                    query_point["type"] !=
                    candidate_point["type"]
                ):
                    continue

                # euclidean distance

                distance = math.sqrt(

                    (
                        query_point["x"] -
                        candidate_point["x"]
                    ) ** 2 +

                    (
                        query_point["y"] -
                        candidate_point["y"]
                    ) ** 2
                )

                # too far apart
                if distance > self.distance_threshold:
                    continue

                # angle difference

                angle_difference = abs(

                    query_point["angle"] -
                    candidate_point["angle"]
                )

                # orientation mismatch
                if (
                    angle_difference >
                    self.angle_threshold
                ):
                    continue


                # match found
                matches.append({

                    "query": {

                        "x": query_point["x"],

                        "y": query_point["y"],

                        "angle": query_point["angle"],

                        "type": query_point["type"]
                    },

                    "candidate": {

                        "x": candidate_point["x"],

                        "y": candidate_point["y"],

                        "angle": candidate_point["angle"],

                        "type": candidate_point["type"]
                    },

                    "distance": distance,

                    "angle_difference": angle_difference
                })

                # mark candidate minutia as used
                used_candidate.add(idx)

                break

        return matches