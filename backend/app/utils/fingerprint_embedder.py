import cv2
import numpy as np

class FingerprintEmbedder:
    """
    Simple deterministic fingerprint embedder.

    Current approach:
    - grayscale
    - resize
    - normalize
    - flatten into fixed-size vector

    Placeholder until real ML model is added.
    """

    def __init__(self, embedding_size: int = 128):
        self.embedding_size = embedding_size

    def extract_embedding(
        self,
        image: np.ndarray
    ):

        # extract embedding from already loaded image.

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