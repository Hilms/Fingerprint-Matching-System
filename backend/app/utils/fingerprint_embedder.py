import cv2
import numpy as np
from skimage.feature import hog, local_binary_pattern
from skimage.morphology import skeletonize
from scipy.signal import convolve2d

"""
this fingerprint system implements multiple classical fingerprint embedding strategies

the goal is to convert a fingerprint image into a fixed-size numerical vector that
can later be used for:

    * similarity search
    * biometric matching
    * indexing
    * retrieval
    * vector database search (pgvector)

the architecture is modular so different embedding strategies can be tested independently
the system currently implements three embedding strategies
"""

class FingerprintEmbedder:

    def __init__(self, embedding_size: int = 128):
        self.embedding_size = embedding_size

    def extract_embedding(
        self,
        image: np.ndarray,
        embedding_method: str
    ):
        """
        methods:
            default
            correlation
            minutiae
            ridge
        """

        if embedding_method == "default":
            return self.default_embedder(image)

        if embedding_method == "correlation":
            return self.correlation_embedder(processed)

        elif embedding_method == "minutiae":
            return self.minutiae_embedder(processed)

        elif embedding_method == "ridge":
            return self.ridge_embedder(processed)

        else:
            raise ValueError(f"Unknown method: {method}")


    def default_embedder(image):

        """
            Simple fingerprint embedder

            Current approach:
            - grayscale
            - resize
            - normalize
            - flatten into fixed-size vector
        """

        # extract embedding from already loaded image
        if image is None:
            raise ValueError("Invalid fingerprint image")

        # ensure grayscale
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # resize
        image = cv2.resize(image, (32, 32))

        # normalize
        image = image.astype(np.float32) / 255.0

        # flatten
        vector = image.flatten()

        # fixed vector size
        if len(vector) > self.embedding_size:
            vector = vector[:self.embedding_size]

        elif len(vector) < self.embedding_size:
            padding = np.zeros(self.embedding_size - len(vector))
            vector = np.concatenate([vector, padding])

        return vector.tolist()


    def preprocess(
        self,
        image: np.ndarray
    ):
        """
        Complete fingerprint preprocessing pipeline.

        Pipeline:
        ---------
        1. grayscale conversion
        2. normalization
        3. segmentation
        4. contrast enhancement (CLAHE)
        5. sharpening
        6. gabor ridge enhancement
        7. binarization
        8. ridge thinning / skeletonization

        Returns:
        --------
        Preprocessed fingerprint image ready for:
            - minutiae extraction
            - ridge analysis
            - embedding generation
        """

        # ensure image exists
        if image is None:
            raise ValueError("Invalid fingerprint image")


        # 1. GRAYSCALE CONVERSION
        # fingerprint processing works on intensity values
        # color information is unnecessary
        #
        # convert:
        #     BGR/RGB -> grayscale
        #
        # result:
        #     single channel image
        #
        # why:
        #     simpler processing
        #     faster computation
        #     better texture analysis

        if len(image.shape) == 3:

            image = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )


        # 2. NORMALIZATION
        # normalize pixel intensity range
        #
        # different scanners/images may have:
        #     - different brightness
        #     - different contrast
        #     - different finger pressure
        #
        # this standardizes the image to:
        #     range 0 -> 255
        #
        # benefits:
        #     more stable feature extraction
        #     better matching consistency

        image = cv2.normalize(
            image,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        image = image.astype(np.uint8)

        # 3. SEGMENTATION
        # remove unnecessary background regions
        #
        # fingerprint images often contain:
        #     - scanner borders
        #     - empty background
        #     - sensor noise
        #
        # we only want:
        #     actual fingerprint area
        #
        # OTSU thresholding automatically finds
        # an optimal separation threshold

        _, mask = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # apply mask to keep only fingerprint region
        image = cv2.bitwise_and(
            image,
            image,
            mask=mask
        )


        # 4. CONTRAST ENHANCEMENT (CLAHE)
        # contrast Limited Adaptive Histogram Equalization
        #
        # enhances local ridge contrast
        #
        # helps with:
        #     - faded fingerprints
        #     - dry skin
        #     - low contrast ridges
        #
        # better than standard histogram equalization
        # because enhancement is local instead of global

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        image = clahe.apply(image)

        # 5. SHARPENING
        # sharpen ridge edges
        #
        # purpose:
        #     make ridge boundaries clearer
        #
        # benefits:
        #     - improved ridge continuity
        #     - better orientation estimation
        #     - improved minutiae extraction

        sharpening_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        image = cv2.filter2D(
            image,
            -1,
            sharpening_kernel
        )


        # 6. GABOR FILTERING
        # gabor filtering is one of the most important
        # fingerprint enhancement techniques
        #
        # fingerprint ridges behave like:
        #     oriented wave patterns
        #
        # gabor filters enhance:
        #     - ridge flow
        #     - ridge continuity
        #
        # while suppressing:
        #     - noise
        #     - broken ridges
        #
        # multiple orientations are used because
        # fingerprint ridges flow in many directions

        image = self.apply_gabor(image)

        # 7. BINARIZATION
        # convert image into binary format
        #
        # result:
        #     ridges -> white
        #     background -> black
        #
        # required for:
        #     - thinning
        #     - minutiae extraction

        _, image = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )


        # 8. INVERSION
        # skeletonization expects:
        #
        #     foreground = white
        #     background = black
        #
        # invert image if necessary.

        image = 255 - image


        # 9. THINNING / SKELETONIZATION
        # convert thick ridge structures into:
        #
        #     1-pixel wide skeletons
        #
        # This is essential for:
        #     - minutiae detection
        #     - ridge ending detection
        #     - bifurcation extraction
        #
        # without thinning:
        #     false minutiae become common

        # convert:
        #     0/255 -> 0/1
        image = image // 255

        # Skeletonize ridge structure
        image = skeletonize(image)

        # Convert back:
        #     0/1 -> 0/255
        image = (image * 255).astype(np.uint8)

        return image


    def apply_gabor(
        self,
        image: np.ndarray
    ):

        accum = np.zeros_like(image, dtype=np.float32)

        for theta in np.arange(0, np.pi, np.pi / 8):

            kernel = cv2.getGaborKernel(
                (21, 21),
                sigma=5,
                theta=theta,
                lambd=10,
                gamma=0.5,
                psi=0,
                ktype=cv2.CV_32F
            )

            filtered = cv2.filter2D(
                image,
                cv2.CV_32F,
                kernel
            )

            accum = np.maximum(accum, filtered)

        accum = cv2.normalize(
            accum,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        return accum.astype(np.uint8)

    def normalize_vector(
        self,
        vector
    ):

        vector = np.array(vector, dtype=np.float32)

        if len(vector) > self.embedding_size:
            vector = vector[:self.embedding_size]

        elif len(vector) < self.embedding_size:

            padding = np.zeros(
                self.embedding_size - len(vector),
                dtype=np.float32
            )

            vector = np.concatenate([vector, padding])

        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        return vector.tolist()


    def correlation_embedder(
        self,
        image: np.ndarray
    ):

        """
        CORRELATION / INTENSITY BASED EMBEDDER

        ## idea
        treat the fingerprint as a texture image
        instead of using raw pixels directly, texture descriptors are extracted

        the implementation currently uses:
        * HOG (Histogram of Oriented Gradients)

        HOG captures:
            * ridge direction
            * local gradient structure
            * edge orientation

        ## advantages
            * simple
            * fast
            * vector database friendly
            * works well with cosine similarity
            * suitable for pgvector similarity search

        ## imitations
            * sensitive to rotation
            * sensitive to translation
            * weaker biometric accuracy than minutiae systems
        """

        image = self.preprocess(image)

        image = cv2.resize(image, (64, 64))

        features = hog(
            image,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            feature_vector=True
        )

        return self.normalize_vector(features)


    def minutiae_embedder(
        self,
        image: np.ndarray
    ):

        """
        MINUTIAE BASED EMBEDDER

        ## Idea
        extract fingerprint landmark points

        main minutiae types:
            * ridge endings
            * ridge bifurcations

        the implementation uses:
            * thinning
            * crossing number algorithm

        ## output vector
        current implementation stores minutiae as: (x, y, type)

        example:

        [
           120, 84, 1,
           90, 44, 3,
           ...
        ]

        where:
            * 1 = ridge ending
            * 3 = bifurcation

        ## advantages
            * classical biometric approach
            * interpretable
            * commonly used in AFIS systems
            * strong biometric meaning

        ## limitations
        this representation is NOT naturally suited for vector similarity databases.

        reason:
            * minutiae are geometric structures
            * spatial relationships matter
            * point alignment matters
            * ordering matters

        two fingerprints may contain:
            * same minutiae
            * different spatial alignment

        which makes dense vector similarity unreliable

        ## why pgvector is weak for minutiae

        vector databases assume:
            * fixed semantic vector dimensions
            * consistent vector geometry

        minutiae are actually
            * unordered point sets
            * geometric graphs

        real minutiae systems usually use:
            * graph matching
            * geometric alignment
            * RANSAC
            * nearest-neighbor correspondence

        instead of cosine vector similarity

        ## current Status
        the current implementation is:
            * educationally correct
            * structurally correct
            * suitable for experimentation

        but not production-grade minutiae matching
        """

        image = self.preprocess(image)

        binary = image // 255

        minutiae = []

        rows, cols = binary.shape

        for y in range(1, rows - 1):
            for x in range(1, cols - 1):

                if binary[y, x] != 1:
                    continue

                neighbors = [
                    binary[y - 1, x],
                    binary[y - 1, x + 1],
                    binary[y, x + 1],
                    binary[y + 1, x + 1],
                    binary[y + 1, x],
                    binary[y + 1, x - 1],
                    binary[y, x - 1],
                    binary[y - 1, x - 1]
                ]

                transitions = 0

                for i in range(8):
                    transitions += abs(
                        neighbors[i] -
                        neighbors[(i + 1) % 8]
                    )

                crossing_number = transitions / 2

                # ridge ending
                if crossing_number == 1:
                    minutiae.extend([x, y, 1])

                # bifurcation
                elif crossing_number == 3:
                    minutiae.extend([x, y, 3])

        features = np.array(minutiae, dtype=np.float32)

        return self.normalize_vector(features)


    def ridge_embedder(
        self,
        image: np.ndarray
    ):

        """
        RIDGE / ORIENTATION BASED EMBEDDER

        ## idea
        analyze global fingerprint ridge structure

        the implementation extracts:
            * ridge orientation histograms
            * local binary pattern texture
            * ridge density

        ## orientation analysis
        using sobel gradients and determining ridge flow orientation captures:
            * ridge direction
            * flow structure
            * global fingerprint layout

        ## LBP texture
        Local Binary Pattern (LBP) captures:
            * local ridge texture
            * micro ridge structures
            * neighborhood patterns

        ## ridge density
        measures:
            * amount of ridge coverage
            * fingerprint occupancy

        ## output vector
        produces a dense vector:

        [
            orientation_histogram,
            lbp_histogram,
            ridge_density
        ]

        ## advantages
            * captures global ridge flow
            * suitable for similarity search
            * more rotation robust than raw texture
            * vector database friendly

        ## limitations
            * still weaker than learned CNN embeddings
            * less precise than advanced minutiae systems

        ## suitability For pgvector
        this method works reasonably well with pgvector because:
            * vectors are dense
            * dimensions are fixed
            * cosine similarity is stable

        """

        image = self.preprocess(image)

        image = image.astype(np.float32)

        # gradients
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1)

        # orientation map
        orientation = np.arctan2(gy, gx)

        orientation_hist, _ = np.histogram(
            orientation,
            bins=32,
            range=(-np.pi, np.pi)
        )

        # local binary pattern texture
        lbp = local_binary_pattern(
            image.astype(np.uint8),
            P=8,
            R=1,
            method="uniform"
        )

        lbp_hist, _ = np.histogram(
            lbp.ravel(),
            bins=32,
            range=(0, 32)
        )

        # ridge density
        density = np.mean(image > 0)

        features = np.concatenate([
            orientation_hist,
            lbp_hist,
            [density]
        ])

        return self.normalize_vector(features)